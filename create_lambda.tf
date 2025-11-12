module "lambda_functions" {
  source                         = "./aws/modules/lambda_function"
  count                          = length(var.lambda_configs)
  short_name                     = var.short_name
  environment                    = var.environment
  reserved_concurrent_executions = try(var.lambda_configs[count.index].reserved_concurrent_executions, 10)
  function_name                  = var.lambda_configs[count.index].function_name
  environment_variables          = var.lambda_configs[count.index].environment_variables
  role_arn                       = var.lambda_execution_role_arn
  file_path                      = var.lambda_configs[count.index].path
  security_group_id              = var.security_group_id
  subnet1                        = var.subnet1
  subnet2                        = var.subnet2
  subnet3                        = var.subnet3
  subnet4                        = var.subnet4
}