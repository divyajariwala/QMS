provider "aws" {
  region = var.region
  default_tags {
    tags = {
      "environment" = "${var.environment}"
      "terraform" = "True"
      "project" = "${var.project}"
      "owner" = "${var.owner}"
      "short_name" = "${var.short_name}"
    }
  }
}