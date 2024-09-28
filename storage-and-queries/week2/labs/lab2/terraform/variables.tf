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

variable "source_data_lake_name" {
  type        = string
  description = "JSON Source Data lake bucket name"
}


variable "curated_db_name" {
  type        = string
  description = "Curated DB name"
  sensitive   = true
}

variable "curated_db_ratings_table" {
  type        = string
  description = "Ratings table at curated DB"
  sensitive   = true
}

variable "curated_db_ml_table" {
  type        = string
  description = "Table for ML at curated DB"
  sensitive   = true
}

variable "presentation_db_name" {
  type        = string
  description = "Presentation zone DB name"
}

variable "presentation_db_table_sales" {
  type        = string
  description = "Sales report table for DA usage at presentation DB"
}

variable "presentation_db_table_employee" {
  type        = string
  description = "Employee report table for DA usage at presentation DB"

}


variable "glue_role_name" {
  type        = string
  description = "Role to be used for glue jobs"
}

variable "ratings_new_column_name" {
  type        = string
  description = "New column name to add to ratings table"
}

variable "ratings_new_column_type" {
  type        = string
  description = "New column type to add to ratings table"
}
