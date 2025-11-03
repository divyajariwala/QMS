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

# locals {
#   api_entries = flatten([
#     for lambda in var.lambda_configs : [
#       for api_path in (try(lambda.api_gateway_paths, []) != null ? lambda.api_gateway_paths : []) : {
#         full_path  = trim(api_path.path_name)           # e.g. "getComplaints" or "getComplaints/{complaint_id}"
#         method     = api_path.http_method
#         lambda_arn = "arn:aws:lambda:${var.region}:${data.aws_caller_identity.current.account_id}:function:${var.short_name}-${var.environment}-${lambda.function_name}"
#         auth       = "NONE"
#       }
#     ]
#   ])

#   # Strict single-segment parents (no slash). Also disallow braces here.
#   api_parents = [
#     for e in local.api_entries : {
#       path_part  = e.full_path
#       method     = e.method
#       lambda_arn = e.lambda_arn
#       auth       = e.auth
#     }
#     if length(split(e.full_path, "/")) == 1
#        && !can(regex("^\\{.*\\}$", e.full_path))        # prevent "{something}" from being a 'parent'
#   ]

#   # Exactly two-segment children (parent/child). Child may be "{id}".
#   api_children = [
#     for e in local.api_entries : {
#       parent_part = split(e.full_path, "/")[0]
#       child_part  = split(e.full_path, "/")[1]
#       method      = e.method
#       lambda_arn  = e.lambda_arn
#       auth        = e.auth
#     }
#     if length(split(e.full_path, "/")) == 2
#   ]

#   # Unique first segments: includes the parents of all children,
#   # plus the plain single-segment routes. This avoids duplicates.
#   parent_segments = toset(concat(
#     [for p in local.api_parents : p.path_part],
#     [for c in local.api_children : c.parent_part]
#   ))
# }

# # ---- PARENTS: one resource per unique first segment ----

# # If the API already has these resources from a previous run (not in TF state),
# # either terraform import them or delete them manually before applying.
# resource "aws_api_gateway_resource" "parent" {
#   for_each    = { for p in local.parent_segments : p => p }

#   rest_api_id = aws_api_gateway_rest_api.api_gateway.id
#   parent_id   = aws_api_gateway_rest_api.api_gateway.root_resource_id
#   path_part   = each.key                                    # e.g., "getComplaints", "createComplaint", etc.
# }

# # Optional: if you want methods/integrations for top-level parents too,
# # drive them from api_parents (not from parent_segments to avoid duplicates).
# module "create_api_parents_methods" {
#   source         = "./aws/modules/api_components"
#   for_each       = { for p in local.api_parents : p.path_part => p }

#   api_gateway_id = aws_api_gateway_rest_api.api_gateway.id
#   parent_id      = aws_api_gateway_resource.parent[each.key].id
#   path_part      = each.value.path_part                      # same as each.key
#   http_method    = each.value.method
#   authorization  = each.value.auth
#   uri            = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${each.value.lambda_arn}/invocations"
#   lambda_arn     = each.value.lambda_arn
#   aws_account_id = data.aws_caller_identity.current.account_id
#   region         = var.region
# }

# # ---- CHILDREN: two-segment paths ----

# # Look up the parent resource by first segment
# data "aws_api_gateway_resource" "parent_by_path" {
#   for_each   = aws_api_gateway_resource.parent
#   rest_api_id = aws_api_gateway_rest_api.api_gateway.id
#   path        = "/${each.key}"
# }

# module "create_api_children" {
#   source = "./aws/modules/api_components"
#   for_each = {
#     for c in local.api_children :
#     "${c.parent_part}/${c.child_part}/${c.method}" => c
#   }

#   api_gateway_id = aws_api_gateway_rest_api.api_gateway.id
#   parent_id      = data.aws_api_gateway_resource.parent_by_path[each.value.parent_part].id
#   path_part      = each.value.child_part                      # e.g., "{complaint_id}"
#   http_method    = each.value.method
#   authorization  = each.value.auth
#   uri            = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${each.value.lambda_arn}/invocations"
#   lambda_arn     = each.value.lambda_arn
#   aws_account_id = data.aws_caller_identity.current.account_id
#   region         = var.region
}
