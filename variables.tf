variable "region" {
  type = string
}

variable "environment" {
  type = string
}

variable "project" {
  type = string
}

variable "short_name" {
  type = string
}

variable "owner" {
  type = string
}

variable "s3_buckets_list" {
  type = list(string)
}

variable "vpc_id" {
  type = string
}

variable "static_website" {
  type = string
}

variable "lambda_execution_role_arn" {
  type = string
}

variable "step_function_role_arn" {
  type = string
}

variable "event_bridge_role_arn" {
  type = string
}

variable "sagemaker_role_arn" {
  type = string
}

variable "openam_tenant_id" {
  type = string
}

variable "openam_client_id" {
  type        = string
}

variable "openam_client_secret" {
  type        = string
  sensitive   = true
}

variable "subnet1" {
  type = string
}

variable "subnet2" {
  type = string
}

variable "subnet3" {
  type = string
}

variable "subnet4" {
  type = string
}

variable "security_group_id" {
  type = string
}

variable "lambda_configs" {
  type = list(object({
    function_name         = string
    path                  = string
    environment_variables = map(string)
    api_gateway_paths = optional(list(object({
      path_name   = string
      http_method = string
    })))
    event_trigger = optional(list(object({
      trigger_name        = string
      trigger_description = string
      trigger_bucket      = string
      trigger_path        = string
    })))
    sqs_trigger = optional(list(object({
      queue_name         = string
      visibility_timeout = number
      max_receive_count  = number
      batch_size         = number
      max_batch_window   = number
      max_concurrency    = number
    })))
  }))
}

variable "serverless_min_acu" {
  description = "Minimum ACUs for Serverless v2 (e.g., 0.5, 1, 2)"
  type        = number
  default     = 0.5
}

variable "serverless_max_acu" {
  description = "Maximum ACUs for Serverless v2"
  type        = number
  default     = 8
}

