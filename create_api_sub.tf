# locals {
#   api_variables = flatten([
#     for lambda in var.lambda_configs : [
#       for api_path in (lambda.api_gateway_paths != null ? lambda.api_gateway_paths : []) : {
#         path_part = api_path.path_name
#         http_method = api_path.http_method
#         lambda_arn = "arn:aws:lambda:${var.region}:${data.aws_caller_identity.current.account_id}:function:${var.short_name}-${var.environment}-${lambda.function_name}"
#         authorization = "NONE"
#       }
#     ]
#   ])
# }

# module "create_api" {
#   depends_on = [ module.lambda_functions ]
#   source = "./aws/modules/api_components"
#   count = length(local.api_variables)
#   api_gateway_id = aws_api_gateway_rest_api.api_gateway.id
#   parent_id = aws_api_gateway_rest_api.api_gateway.root_resource_id
#   path_part = local.api_variables[count.index].path_part
#   http_method = local.api_variables[count.index].http_method
#   authorization = local.api_variables[count.index].authorization
#   uri = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${local.api_variables[count.index].lambda_arn}/invocations"
#   lambda_arn = local.api_variables[count.index].lambda_arn
#   aws_account_id = data.aws_caller_identity.current.account_id
#   region = var.region
# } 

locals {
  # Flatten inputs (unchanged idea)
  api_entries = flatten([
    for lambda in var.lambda_configs : [
      for api_path in (lambda.api_gateway_paths != null ? lambda.api_gateway_paths : []) : {
        full_path  = api_path.path_name
        method     = api_path.http_method
        lambda_arn = "arn:aws:lambda:${var.region}:${data.aws_caller_identity.current.account_id}:function:${var.short_name}-${var.environment}-${lambda.function_name}"
        auth       = "NONE"
      }
    ]
  ])

  # Parents: single-segment paths only (no slash)
  api_parents = [
    for e in local.api_entries : {
      path_part  = e.full_path
      method     = e.method
      lambda_arn = e.lambda_arn
      auth       = e.auth
    }
    if length(split(e.full_path, "/")) == 1
  ]

  # Children: exactly two segments
  api_children = [
    for e in local.api_entries : {
      parent_part = split(e.full_path, "/")[0]   # "getComplaints"
      child_part  = split(e.full_path, "/")[1]   # "{complaint_id}"
      method      = e.method
      lambda_arn  = e.lambda_arn
      auth        = e.auth
    }
    if length(split(e.full_path, "/")) == 2
  ]

  # Unique *first* segments only — these are the real parents
  parent_segments = toset([for e in local.api_entries : split(e.full_path, "/")[0]])
}

# Create parents
module "create_api_parents" {
  depends_on     = [module.lambda_functions]
  source         = "./aws/modules/api_components"
  count          = length(local.api_parents)

  api_gateway_id = aws_api_gateway_rest_api.api_gateway.id
  parent_id      = aws_api_gateway_rest_api.api_gateway.root_resource_id
  path_part      = local.api_parents[count.index].path_part
  http_method    = local.api_parents[count.index].method
  authorization  = local.api_parents[count.index].auth
  uri            = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${local.api_parents[count.index].lambda_arn}/invocations"
  lambda_arn     = local.api_parents[count.index].lambda_arn
  aws_account_id = data.aws_caller_identity.current.account_id
  region         = var.region
}

# Look up parents by path (ONLY first segments)
data "aws_api_gateway_resource" "parent_by_path" {
  depends_on  = [module.create_api_parents] # ensure they exist
  for_each    = { for p in local.parent_segments : p => p }
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  path        = "/${each.key}"              # e.g. "/getComplaints"
}

# Create children
module "create_api_children" {
  depends_on     = [module.create_api_parents]
  source         = "./aws/modules/api_components"
  count          = length(local.api_children)

  api_gateway_id = aws_api_gateway_rest_api.api_gateway.id
  parent_id      = data.aws_api_gateway_resource.parent_by_path[
                     local.api_children[count.index].parent_part
                   ].id
  path_part      = local.api_children[count.index].child_part   # "{complaint_id}"
  http_method    = local.api_children[count.index].method
  authorization  = local.api_children[count.index].auth
  uri            = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${local.api_children[count.index].lambda_arn}/invocations"
  lambda_arn     = local.api_children[count.index].lambda_arn
  aws_account_id = data.aws_caller_identity.current.account_id
  region         = var.region
}

