resource "aws_sagemaker_model" "sagemaker_model" {
  name = var.model_name
  execution_role_arn = var.sagemaker_execution_role_arn
  primary_container {
    image = var.sagemaker_image_uri
    model_data_url = var.model_data_url
    mode = "SingleModel"
  }
  vpc_config {
    subnets = var.subnets
    security_group_ids = var.security_group_ids
  }
}

resource "aws_sagemaker_endpoint_configuration" "sagemaker_endpoint_config" {
  name = var.endpoint_config_name
  production_variants {
    variant_name = "AllTraffic"
    model_name = aws_sagemaker_model.sagemaker_model.name
    initial_instance_count = 1
    instance_type = var.instance_type
    initial_variant_weight = 1.0
  }
}

resource "aws_sagemaker_endpoint" "sagemaker_endpoint" {
  name = var.endpoint_name
  endpoint_config_name = aws_sagemaker_endpoint_configuration.sagemaker_endpoint_config.name
}