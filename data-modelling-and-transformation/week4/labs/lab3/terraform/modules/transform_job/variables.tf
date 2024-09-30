variable "project" {
  type        = string
  description = "Project name"
}

variable "region" {
  type        = string
  description = "AWS Region"
}

variable "glue_role_arn" {
  type        = string
  description = "ARN for glue jobs execution"
}

variable "scripts_bucket_name" {
  type        = string
  description = "S3 Bucket for glue scripts storage"
}

variable "data_lake_name" {
  type        = string
  description = "S3 Bucket for glue scripts storage"
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
