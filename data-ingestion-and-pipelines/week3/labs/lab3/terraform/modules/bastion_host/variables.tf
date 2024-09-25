# Include the definition of the variables you will use throughout the
# definition of resources.

variable "project" {
  type        = string
  description = "The name of the project"
  default     = "de-c2w3lab2"
}

variable "region" {
  type        = string
  description = "The AWS region to use for provisioning"
  default     = "us-east-1"
}

variable "vpc_id" {
  type        = string
  description = "The id of the VPC to use"
}

variable "public_subnet_a_id" {
  type        = string
  description = "The id of the public subnet in the availability zone A"
}

variable "public_subnet_b_id" {
  type        = string
  description = "The id of the public subnet in the availability zone B"
}

variable "private_subnet_a_id" {
  type        = string
  description = "The id of the private subnet in the availability zone A"
}

variable "private_subnet_b_id" {
  type        = string
  description = "The id of the private subnet in the availability zone B"
}

variable "db_master_username" {
  type        = string
  description = "The master username for the RDS instance"
  default     = "postgres_admin"
}
