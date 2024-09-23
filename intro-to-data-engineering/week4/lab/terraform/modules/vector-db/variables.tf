variable "project" {
  type        = string
  description = "Project name"
}

variable "region" {
  type        = string
  description = "AWS Region"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID"
}

variable "public_subnet_a_id" {
  type        = string
  description = "Public subnet in AZ A ID"
}

variable "public_subnet_b_id" {
  type        = string
  description = "Public subnet in AZ B ID"
}

variable "master_username" {
  type        = string
  description = "Master username for RDS"
  default     = "postgres"
}
