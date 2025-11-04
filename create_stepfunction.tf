module "complaints_step_function" {
  source = "./aws/modules/step_function"
  count = length(var.step_function_configs)
  state_machine_name = "${var.short_name}-${var.environment}-${var.step_function_configs[count.index].step_function_name}"
  role_arn = var.step_function_role_arn
  definition_config = "conf/definitions/${var.step_function_configs[count.index].step_function_name}.json.tftpl"
  definition_vars = {
    region      = var.region
    account_id     = data.aws_caller_identity.current.account_id
    short_name  = var.short_name
    environment = var.environment
    complaints_level_function_name = "calculate-complaints-level"
    complaints_subcat_function_name = "calculate-complaints-subcategory"
    complaints_crl_function_name = "calculate-complaints-crl"
    complaints_priority_function_name = "calculate-complaints-priority"
  }
}