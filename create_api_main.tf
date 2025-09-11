resource "aws_api_gateway_rest_api" "api_gateway" {
  name = "${var.short_name}-${var.environment}-api"
  endpoint_configuration {
    types = ["EDGE"]
  }
  binary_media_types = ["image/png", "application/pdf", "application/octet-stream"]
}

resource "aws_api_gateway_deployment" "api_deployment" {
  depends_on = [module.create_api]
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  lifecycle {
    create_before_destroy = true
  }
  variables = {
    deployed_on = formatdate("YYYYMMDD_hh:mm:ss", timestamp())
  }
}

resource "aws_api_gateway_stage" "api_stage" {
  deployment_id = aws_api_gateway_deployment.api_deployment.id
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  stage_name = var.environment
}