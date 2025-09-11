resource "aws_lambda_permission" "lambda_permission" {
  function_name = var.lambda_arn
  action = "lambda:InvokeFunction"
  principal = "apigateway.amazonaws.com"
  source_arn = "arn:aws:execute-api:${var.region}:${var.aws_account_id}:${var.api_gateway_id}/*/*/${var.path_part}"
}

resource "aws_api_gateway_resource" "api_resource" {
  rest_api_id = var.api_gateway_id
  parent_id = var.parent_id
  path_part = var.path_part
}

resource "aws_api_gateway_method" "api_method" {
  depends_on = [aws_api_gateway_resource.api_resource]
  rest_api_id = var.api_gateway_id
  resource_id = aws_api_gateway_resource.api_resource.id
  http_method = var.http_method
  authorization = var.authorization
}

resource "aws_api_gateway_integration" "method_integration" {
  depends_on = [aws_api_gateway_method.api_method]
  rest_api_id = var.api_gateway_id
  resource_id = aws_api_gateway_resource.api_resource.id
  http_method = var.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = var.uri
  passthrough_behavior = "WHEN_NO_MATCH"
}

resource "aws_api_gateway_method_response" "method_response" {
  depends_on = [aws_api_gateway_integration.method_integration]
  rest_api_id = var.api_gateway_id
  resource_id = aws_api_gateway_resource.api_resource.id
  http_method = var.http_method
  status_code = 200
  response_models = {
    "application/json" = "Empty"
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "integration_response" {
  depends_on = [aws_api_gateway_method_response.method_response]
  rest_api_id = var.api_gateway_id
  resource_id = aws_api_gateway_resource.api_resource.id
  http_method = var.http_method
  status_code = 200
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,session-uuid,query-md5'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

resource "aws_api_gateway_method" "options_method" {
  depends_on = [aws_api_gateway_resource.api_resource]
  rest_api_id = var.api_gateway_id
  resource_id = aws_api_gateway_resource.api_resource.id
  http_method = "OPTIONS"
  authorization = var.authorization
}

resource "aws_api_gateway_integration" "options_integration" {
  depends_on = [aws_api_gateway_method.options_method]
  rest_api_id = var.api_gateway_id
  resource_id = aws_api_gateway_resource.api_resource.id
  http_method = "OPTIONS"
  type = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "options_method_response" {
  depends_on = [aws_api_gateway_integration.options_integration]
  rest_api_id = var.api_gateway_id
  resource_id = aws_api_gateway_resource.api_resource.id
  http_method = "OPTIONS"
  status_code = 200
  response_models = {
    "application/json" = "Empty"
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "options_integration_response" {
  depends_on = [aws_api_gateway_method_response.options_method_response]
  rest_api_id = var.api_gateway_id
  resource_id = aws_api_gateway_resource.api_resource.id
  http_method = "OPTIONS"
  status_code = 200
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,session-uuid,query-md5'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}