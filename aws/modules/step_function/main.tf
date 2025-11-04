data "template_file" "read_definition_file" {
  template = file(var.definition_config)
  vars     = var.definition_vars
}

resource "aws_cloudwatch_log_group" "log_group_for_sfn" {
  name              = var.state_machine_name
  retention_in_days = 365
}

resource "aws_sfn_state_machine" "state_machine" {
  name       = var.state_machine_name
  role_arn   = var.role_arn
  type       = "STANDARD"
  definition = data.template_file.read_definition_file.rendered

  logging_configuration {
    level                  = "ALL"
    include_execution_data = true
    # Step Functions requires the :* suffix
    log_destination        = "${aws_cloudwatch_log_group.log_group_for_sfn.arn}:*"
  }

  tracing_configuration {
    enabled = true
  }
}
