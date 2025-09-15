locals {
  # managed_layer_arn = "arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python39:28"
  # custom_layer_name = "insights-requests-toolbelt-layer"
}

# resource "aws_s3_object" "custom_layer_zip" {
#   bucket = module.all_s3_buckets[2].s3_bucket_name
#   key = "${local.custom_layer_name}.zip"
#   source = "conf/dev/layers/${local.custom_layer_name}.zip"
#   etag = filemd5("conf/dev/layers/${local.custom_layer_name}.zip")
# }

# resource "aws_lambda_layer_version" "custom_layer" {
#   layer_name = "${local.custom_layer_name}"
#   s3_bucket = module.all_s3_buckets[2].s3_bucket_name
#   s3_key = aws_s3_object.custom_layer_zip.key
#   compatible_runtimes = ["python3.9"]
#   compatible_architectures = [ "x86_64" ]
# }

# module "lambda_functions" {
#   source = "./aws/modules/lambda_function"
#   count = length(var.lambda_configs)
#   short_name = var.short_name
#   environment = var.environment
#   function_name = var.lambda_configs[count.index].function_name
#   environment_variables = var.lambda_configs[count.index].environment_variables
#   role_arn = var.lambda_execution_role_arn
#   file_path = var.lambda_configs[count.index].path
#   security_group_id = ""
#   subnet1 = var.subnet1
#   subnet2 = var.subnet2
#   subnet3 = var.subnet3
#   subnet4 = var.subnet4
#   # custom_layer_arn = aws_lambda_layer_version.custom_layer.arn
#   # managed_layer_arn = local.managed_layer_arn
# }