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

variable "db_sg_id" {
  type        = string
  description = "Security group ID for RDS"
}

variable "source_host" {
  type        = string
  description = "RDS host"
}

variable "source_port" {
  type        = number
  description = "RDS port"
  default     = 3306
}

variable "source_database" {
  type        = string
  description = "RDS database name"
}

variable "source_username" {
  type        = string
  description = "RDS username"
}

variable "source_password" {
  type        = string
  description = "RDS password"
  sensitive   = true
}

variable "data_lake_name" {
  type        = string
  description = "Data lake bucket name"
}

variable "catalog_database" {
  type        = string
  description = "Curated DB name"
  sensitive   = true
}

variable "users_table" {
  type        = string
  description = "Table to store users data"
  sensitive   = true
}

variable "sessions_table" {
  type        = string
  description = "Table to store sessions data"
  sensitive   = true
}

variable "songs_table" {
  type        = string
  description = "Table to store songs data"
  sensitive   = true
}

variable "redshift_role_name" {
  type        = string
  description = "Role for Redshift spectrum"
}

variable "redshift_host" {
  type        = string
  description = "Redshift host"
}

variable "redshift_user" {
  type        = string
  description = "Redshift user"
}

variable "redshift_password" {
  type        = string
  description = "Redshift user's password"
}

variable "redshift_database" {
  type        = string
  description = "Redshift database"
}

variable "redshift_port" {
  type        = number
  description = "Redshift port"
}
