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
  rule = aws_cloudwatch_event_rule.event_rule.name
  arn  = var.lambda_arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.event_rule.arn
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket      = var.trigger_bucket
  eventbridge = true
}