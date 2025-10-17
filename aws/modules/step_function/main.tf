data "template_file" "read_definition_file" {
  template = file(var.definition_config)
  vars = {
    region = var.region
    account = var.account
    short_name = var.short_name
    environment = var.environment
  }
}

resource "aws_sfn_state_machine" "state_machine" {
  name = var.state_machine_name
  role_arn = var.role_arn
  definition = data.template_file.read_definition_file.rendered
  logging_configuration {
    level = "ALL"
    include_execution_data = true
    log_destination = "${aws_cloudwatch_log_group.log_group_for_sfn.arn}:*"
  }
  tracing_configuration {
    enabled = true
  }
}

resource "aws_cloudwatch_log_group" "log_group_for_sfn" {
  name = var.state_machine_name
  retention_in_days = 365
}