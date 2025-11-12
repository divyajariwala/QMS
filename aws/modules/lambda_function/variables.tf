variable "short_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "function_name" {
  type = string
}

variable "role_arn" {
  type = string
}

variable "file_path" {
  type = string
}

variable "security_group_id" {
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

variable "environment_variables" {
  type    = map(string)
  default = {}
}

variable "reserved_concurrent_executions" {
  type = string
}