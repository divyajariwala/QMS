module "step_function" {
  source = "./aws/modules/step_function"
  count = length(var.step_function_configs)
  state_machine_name = "${var.short_name}-${var.environment}-${var.step_function_configs[count.index].step_function_name}"
  role_arn = var.step_function_role_arn
  definition_config = "conf/dev/definitions/${var.step_function_configs[count.index].step_function_name}.json"
  region = var.region
  short_name = var.short_name
  environment = var.environment
  account = data.aws_caller_identity.current.account_id
}