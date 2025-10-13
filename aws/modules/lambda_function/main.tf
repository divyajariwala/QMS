resource "aws_lambda_function" "lambda_function" {
  function_name = "${var.short_name}-${var.environment}-${var.function_name}"
  handler = "lambda_function.lambda_handler"
  runtime = "python3.9"
  role  = var.role_arn
  filename = "${var.file_path}.zip"
  source_code_hash = filebase64sha256("${var.file_path}.zip")
  timeout = 900
  memory_size = 10240
  vpc_config {
    security_group_ids = [var.security_group_id]
    subnet_ids = [var.subnet1, var.subnet2, var.subnet3, var.subnet4]
  }
  tracing_config {
    mode = "Active"
  }
  environment {
    variables = var.environment_variables
  }
  kms_key_arn = var.kms_key_arn
  reserved_concurrent_executions = var.reserved_concurrent_executions
}