resource "aws_sqs_queue" "dead_letter_queue" {
  name = "${var.queue_name}-dlq"
  sqs_managed_sse_enabled = true
  message_retention_seconds = 1209600
}

resource "aws_sqs_queue" "sqs_queue" {
  name = var.queue_name
  sqs_managed_sse_enabled = true
  visibility_timeout_seconds = var.visibility_timeout
  redrive_policy = jsonencode({
    deadLetterTargetArn = "${aws_sqs_queue.dead_letter_queue.arn}"
    maxReceiveCount = "${var.max_receive_count}"
  })
}

resource "aws_lambda_event_source_mapping" "lambda_mapping" {
  event_source_arn = aws_sqs_queue.sqs_queue.arn
  function_name = var.lambda_function_name
  batch_size = var.batch_size
  maximum_batching_window_in_seconds = var.max_batch_window
  scaling_config {
    maximum_concurrency = var.max_concurrency
  }
}