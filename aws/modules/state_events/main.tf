resource "aws_cloudwatch_event_rule" "event_rule" {
  name           = var.trigger_name
  description    = var.trigger_description
  event_bus_name = "default"
  event_pattern = jsonencode({
    "detail-type" = ["Object Created"],
    "source"      = ["aws.s3"],
    "detail" = {
      "bucket" = {
        "name" = ["${var.trigger_bucket}"]
      },
      "object" = {
        "key" = [{
          "wildcard" = "${var.trigger_path}"
        }]
      }
    }
  })
}

resource "aws_cloudwatch_event_target" "event_target" {
  rule     = aws_cloudwatch_event_rule.event_rule.name
  arn      = var.step_function_arn
  role_arn = var.event_bridge_role_arn
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket      = var.trigger_bucket
  eventbridge = true
}