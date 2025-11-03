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
  # Flatten your lambda_configs into simple entries
  api_entries = flatten([
    for lambda in var.lambda_configs : [
      for api_path in (lambda.api_gateway_paths != null ? lambda.api_gateway_paths : []) : {
        full_path   = api_path.path_name                    # e.g., "getComplaints" or "getComplaints/{complaint_id}"
        method      = api_path.http_method                  # e.g., "GET"
        lambda_arn  = "arn:aws:lambda:${var.region}:${data.aws_caller_identity.current.account_id}:function:${var.short_name}-${var.environment}-${lambda.function_name}"
        auth        = "NONE"
      }
    ]
  ])

  # Parents: paths with ONE segment (no slash)
  api_parents = [
    for e in local.api_entries :
    {
      path_part   = e.full_path                             # e.g., "getComplaints"
      method      = e.method
      lambda_arn  = e.lambda_arn
      auth        = e.auth
    }
    if length(split(e.full_path, "/")) == 1
  ]

  # Children: paths with TWO segments (exactly one slash)
  # If you need deeper nesting later, see the note at the end to generalize.
  api_children = [
    for e in local.api_entries : {
      parent_part = split(e.full_path, "/")[0]              # e.g., "getComplaints"
      child_part  = split(e.full_path, "/")[1]              # e.g., "{complaint_id}"
      method      = e.method
      lambda_arn  = e.lambda_arn
      auth        = e.auth
    }
    if length(split(e.full_path, "/")) == 2
  ]
}

module "create_api_parents" {
  depends_on     = [ module.lambda_functions ]
  source         = "./aws/modules/api_components"
  count          = length(local.api_parents)

  api_gateway_id = aws_api_gateway_rest_api.api_gateway.id
  parent_id      = aws_api_gateway_rest_api.api_gateway.root_resource_id
  path_part      = local.api_parents[count.index].path_part               # e.g., "getComplaints"
  http_method    = local.api_parents[count.index].method
  authorization  = local.api_parents[count.index].auth
  uri            = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${local.api_parents[count.index].lambda_arn}/invocations"
  lambda_arn     = local.api_parents[count.index].lambda_arn
  aws_account_id = data.aws_caller_identity.current.account_id
  region         = var.region
}

# Unique parent paths to avoid duplicate lookups
locals {
  parent_path_set = toset([for p in local.api_parents : p.path_part])
}

data "aws_api_gateway_resource" "parent_by_path" {
  for_each   = { for p in local.parent_path_set : p => p }
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  path        = "/${each.key}"                 # e.g., "/getComplaints"
}

module "create_api_children" {
  depends_on     = [ module.create_api_parents ]           # ensure parent exists
  source         = "./aws/modules/api_components"
  count          = length(local.api_children)

  api_gateway_id = aws_api_gateway_rest_api.api_gateway.id

  # parent_id is the ID of /<parent_part>
  parent_id      = data.aws_api_gateway_resource.parent_by_path[
                     local.api_children[count.index].parent_part
                   ].id

  path_part      = local.api_children[count.index].child_part            # e.g., "{complaint_id}"
  http_method    = local.api_children[count.index].method
  authorization  = local.api_children[count.index].auth
  uri            = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${local.api_children[count.index].lambda_arn}/invocations"
  lambda_arn     = local.api_children[count.index].lambda_arn
  aws_account_id = data.aws_caller_identity.current.account_id
  region         = var.region
}
