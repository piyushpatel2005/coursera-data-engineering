# Configure the backend for Terraform using AWS
terraform {
  backend "s3" {
    ### START CODE HERE ### (~ 4 lines of code)
    bucket         = <terraform_state_bucket> # The name of the S3 bucket to store the state file
    key            = "de-c2w3lab2/terraform.state" # The key in the bucket
  # where the state file will be stored
    region         = "us-east-1"
    encrypt        = true
    
  }
}
