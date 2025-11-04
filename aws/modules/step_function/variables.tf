variable "definition_config" {
  description = "Path to the ASL template file (e.g., definition.json.tftpl)"
  type        = string
}

variable "definition_vars" {
  description = "Map of variables for the ASL template"
  type        = map(string)
}

variable "state_machine_name" {
  type        = string
  description = "Step Functions state machine name"
}

variable "role_arn" {
  type        = string
  description = "IAM role ARN for the state machine"
}