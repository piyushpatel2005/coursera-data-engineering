terraform {
  required_providers {
    redshift = {
      source  = "brainly/redshift"
      version = ">= 0.2.4"
    }
  }
}

provider "redshift" {
  alias    = "default"
  host     = var.redshift_host
  username = var.redshift_user
  password = var.redshift_password
  database = var.redshift_database
  port     = var.redshift_port
}
