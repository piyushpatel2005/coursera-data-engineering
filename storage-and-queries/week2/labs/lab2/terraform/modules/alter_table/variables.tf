variable "project" {
  type        = string
  description = "Project name"
}

variable "region" {
  type        = string
  description = "AWS region"
}

variable "glue_role_arn" {
  type        = string
  description = "Table for ML at curated DB"
}

variable "data_lake_name" {
  type        = string
  description = "Data lake bucket name"
}

variable "scripts_bucket_name" {
  type        = string
  description = "Glue Scripts bucket name"
}

variable "curated_db_name" {
  type        = string
  description = "Curated DB name"
}

variable "curated_db_ratings_table" {
  type        = string
  description = "Ratings table at curated DB"
}

variable "ratings_new_column_name" {
  type        = string
  description = "New column name to add to ratings table"
}

variable "ratings_new_column_type" {
  type        = string
  description = "New column type to add to ratings table"
}
