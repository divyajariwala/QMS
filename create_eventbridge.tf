locals {
  event_configurations = flatten([
    for lambda in var.lambda_configs : [
      for event_details in (lambda.event_trigger != null ? lambda.event_trigger : []) : {
        trigger_name = event_details.trigger_name
        trigger_description = event_details.trigger_description
        trigger_bucket = event_details.trigger_bucket
        trigger_path = event_details.trigger_path
        lambda_arn = "arn:aws:lambda:${var.region}:${data.aws_caller_identity.current.account_id}:function:${var.short_name}-${var.environment}-${lambda.function_name}"
        lambda_name = "${var.short_name}-${var.environment}-${lambda.function_name}"
      }
    ]
  ])
  state_configurations = flatten([
    for state in var.step_function_configs : [
      for event_details in try(state.event_trigger, []) : {  # Fix applied
        trigger_name = event_details.trigger_name
        trigger_description = event_details.trigger_description
        trigger_bucket = event_details.trigger_bucket
        trigger_path = event_details.trigger_path
        step_function_arn = "arn:aws:states:${var.region}:${data.aws_caller_identity.current.account_id}:stateMachine:${var.short_name}-${var.environment}-${state.step_function_name}"
      }
    ]
  ])
}

module "create_events_lambda" {
  depends_on = [ module.lambda_functions ]
  source = "./aws/modules/lambda_events"
  count = length(local.event_configurations)
  trigger_name = local.event_configurations[count.index].trigger_name
  trigger_description = local.event_configurations[count.index].trigger_description
  trigger_bucket = local.event_configurations[count.index].trigger_bucket
  trigger_path = local.event_configurations[count.index].trigger_path
  lambda_arn = local.event_configurations[count.index].lambda_arn
  lambda_name = local.event_configurations[count.index].lambda_name
}

module "create_events_states" {
  depends_on = [ module.step_function ]
  source = "./aws/modules/state_events"
  count = length(local.state_configurations)
  trigger_name = local.state_configurations[count.index].trigger_name
  trigger_description = local.state_configurations[count.index].trigger_description
  trigger_bucket = local.state_configurations[count.index].trigger_bucket
  trigger_path = local.state_configurations[count.index].trigger_path
  step_function_arn = local.state_configurations[count.index].step_function_arn 
  event_bridge_role_arn = var.event_bridge_role_arn
}