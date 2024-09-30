variable "project" {
  type        = string
  description = "Project name"
}

variable "region" {
  type        = string
  description = "AWS Region"
}

variable "catalog_database" {
  type        = string
  description = "Curated DB name"
  sensitive   = true
}