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

variable "curated_db_ml_table" {
  type        = string
  description = "Table for ML at curated DB"

}

variable "glue_role_arn" {
  type        = string
  description = "Table for ML at curated DB"
}
