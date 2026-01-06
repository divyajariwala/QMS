locals {
  sagemaker_endpoints = {
    mounjaro_level = {
      name = "${var.short_name}-${var.environment}-mounjaro-level"
      image_uri = "763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-inference:2.1.0-transformers4.37.0-gpu-py310-cu118-ubuntu20.04"
      s3_file_path = "s3://${var.short_name}-${var.environment}-model-files/mounjaro-level-model.tar.gz"
      instance_type = "ml.g4dn.xlarge"
      execution_role_arn = var.sagemaker_role_arn
      subnet_ids = [var.subnet1, var.subnet2]
      security_group_ids = [var.security_group_id]
    }
    mounjaro_category = {
      name = "${var.short_name}-${var.environment}-mounjaro-category"
      image_uri = "763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-inference:2.1.0-transformers4.37.0-gpu-py310-cu118-ubuntu20.04"
      s3_file_path = "s3://${var.short_name}-${var.environment}-model-files/mounjaro-category-model.tar.gz"
      instance_type = "ml.g4dn.xlarge"
      execution_role_arn = var.sagemaker_role_arn
      subnet_ids = [var.subnet1, var.subnet2]
      security_group_ids = [var.security_group_id]
    }
  }
}

module "sagemaker_endpoints" {
  source = "./aws/modules/sagemaker"
  for_each = local.sagemaker_endpoints
  model_name = each.value.name
  endpoint_config_name = each.value.name
  endpoint_name = each.value.name
  sagemaker_image_uri = each.value.image_uri
  model_data_url = each.value.s3_file_path
  instance_type = each.value.instance_type
  sagemaker_execution_role_arn = each.value.execution_role_arn
  subnets = each.value.subnet_ids
  security_group_ids = each.value.security_group_ids
}