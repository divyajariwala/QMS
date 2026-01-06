variable model_name {
    type = string
}

variable sagemaker_execution_role_arn {
    type = string
}

variable sagemaker_image_uri {
    type = string
}

variable subnets {
    type = list(string)
}

variable security_group_ids {
    type = list(string)
}

variable endpoint_config_name {
    type = string
}

variable instance_type {
    type = string
}

variable endpoint_name {
    type = string
}

variable model_data_url {
  type = string
}