variable "project" {
  type        = string
  description = "Project name"
}

variable "region" {
  type        = string
  description = "AWS region"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID"
}

variable "private_subnet_a_id" {
  type        = string
  description = "Private subnet A ID"
}

variable "data_lake_name" {
  type        = string
  description = "Data lake bucket name"
}
