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