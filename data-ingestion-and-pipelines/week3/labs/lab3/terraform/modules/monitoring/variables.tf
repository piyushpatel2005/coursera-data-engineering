variable "project" {
  type        = string
  description = "The name of the project"
  default     = "de-c2w3lab1"
}

variable "region" {
  type        = string
  description = "The AWS region to use for provisioning"
  default     = "us-east-1"
}

variable "bastion_host_id" {
  type        = string
  description = "The ID from Bastion"
}

variable "notification_email" {
  type        = string
  description = "An email to receive the CloudWatch alarm message"
}

variable "rds_instance_id" {
  type        = string
  description = "RDS Instance ID"
}
