terraform {
  backend "s3" {
    bucket         = "de-c4w4a2-767397743417-us-east-1-terraform-state"
    key            = "de-c4w4/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
  }
}