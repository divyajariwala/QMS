variable "queue_name" {
  type = string
}

variable "visibility_timeout" {
  type = number
}

variable "max_receive_count" {
  type = number
}

variable "lambda_function_name" {
  type = string
}

variable "batch_size" {
  type = number
}

variable "max_batch_window" {
  type = number
}

variable "max_concurrency" {
  type = number
}