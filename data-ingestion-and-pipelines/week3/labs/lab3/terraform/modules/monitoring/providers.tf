# Define the versions and configurations of the providers

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.39.1"
    }
    local = {
      source  = "hashicorp/local"
      version = "2.4.1"
    }
    random = {
      source  = "hashicorp/random"
      version = "= 3.6.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "4.0.5"
    }
  }
}

# Add to the provider configuration the tags and
# parameters needed
provider "aws" {
  region = var.region
  default_tags {
    tags = {
      comments  = "this resource is managed by terraform"
      terraform = "true"
      project   = var.project
    }
  }
}
