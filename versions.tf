terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.85.0"
    }
  }
  backend "s3" {
    bucket = "qms-dev-tfstate"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}