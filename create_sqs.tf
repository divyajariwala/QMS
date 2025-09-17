locals {
  sqs_variables = flatten([
    for lambda in var.lambda_configs : [
      for sqs_trigger in (lambda.sqs_trigger != null ? lambda.sqs_trigger : []) : {
        queue_name = sqs_trigger.queue_name
        visibility_timeout = sqs_trigger.visibility_timeout
        max_receive_count = sqs_trigger.max_receive_count
        batch_size = sqs_trigger.batch_size
        max_batch_window = sqs_trigger.max_batch_window
        max_concurrency = sqs_trigger.max_concurrency
        lambda_arn = "arn:aws:lambda:${var.region}:${data.aws_caller_identity.current.account_id}:function:${var.short_name}-${var.environment}-${lambda.function_name}"
        lambda_name = "${var.short_name}-${var.environment}-${lambda.function_name}"
      }
    ]
  ])
}

module "create_sqs_lambda" {
  depends_on = [ module.lambda_functions ]
  source = "./aws/modules/lambda_sqs"
  queue_name = local.sqs_variables[count.index].queue_name
  visibility_timeout = local.sqs_variables[count.index].visibility_timeout
  max_receive_count = local.sqs_variables[count.index].max_receive_count
  lambda_function_name = local.sqs_variables[count.index].lambda_name
  batch_size = local.sqs_variables[count.index].batch_size
  max_batch_window = local.sqs_variables[count.index].max_batch_window
  max_concurrency = local.sqs_variables[count.index].max_concurrency
}