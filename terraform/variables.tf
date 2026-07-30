variable "aws_region" {
  type        = string
  default     = "eu-west-1"
  description = "AWS deployment region"
}

variable "environment" {
  type        = string
  default     = "staging"
  description = "Target deployment environment"
}

variable "vpc_cidr" {
  type        = string
  default     = "10.0.0.0/16"
  description = "Base VPC CIDR block"
}