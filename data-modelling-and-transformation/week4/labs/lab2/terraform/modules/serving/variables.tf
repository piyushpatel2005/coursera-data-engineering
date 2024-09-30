variable "project" {
  type        = string
  description = "Project name"
}

variable "region" {
  type        = string
  description = "AWS Region"
}

variable "redshift_role_name" {
  type        = string
  description = "Role name for redshift spectrum"
}

variable "catalog_database" {
  type        = string
  description = "Curated DB name"
  sensitive   = true
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
