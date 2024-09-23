variable "project" {
  type        = string
  description = "Project name"
}

variable "region" {
  type        = string
  description = "AWS Region"
}

variable "private_subnet_a_id" {
  type        = string
  description = "Private subnet A ID"
}

variable "db_sg_id" {
  type        = string
  description = "Security group ID for RDS"
}

variable "host" {
  type        = string
  description = "RDS host"
}

variable "port" {
  type        = number
  description = "RDS port"
  default     = 3306
}

variable "database" {
  type        = string
  description = "RDS database name"
}

variable "username" {
  type        = string
  description = "RDS username"
}

variable "password" {
  type        = string
  description = "RDS password"
  sensitive   = true
}
