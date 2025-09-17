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

variable "ecs_task_role_arn" {
  type = string
}

variable "ecs_openai_api_key" {
  type = string
}

variable "ecs_openai_base_url" {
  type = string
}

variable "sagemaker_endpoint_name" {
  type = string
}

variable "api_image_uri" {
  type = string
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
    function_name = string
    path = string
    environment_variables = map(string)
    api_gateway_paths = optional(list(object({
      path_name = string
      http_method = string
    })))
    event_trigger = optional(list(object({
      trigger_name = string
      trigger_description = string
      trigger_bucket = string
      trigger_path = string
    })))
    sqs_trigger = optional(list(object({
      queue_name = string
      visibility_timeout = number
      max_receive_count = number
      batch_size = number
      max_batch_window = number
      max_concurrency = number
    }))) 
  }))
}

# variable "step_function_configs" {
#   type = list(object({
#     step_function_name = string
#     definition_yaml_path = string
#     event_trigger = optional(list(object({
#       trigger_name = string
#       trigger_description = string
#       trigger_bucket = string
#       trigger_path = string
#     })))
#   }))
# }

# variable "dynamodb_configs" {    
#   type = list(object({  
#     table_name = string  
#     part_key = object({  
#       key_name = string  
#       key_type = string  
#     })  
#     sort_key = optional(object({  
#       key_name = string  
#       key_type = string  
#     }))  
#   }))  

# } 
