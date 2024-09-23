#!/bin/bash
set -e
export de_project="de-c1w4"
export AWS_DEFAULT_REGION="us-east-1"
export VPC_ID=$(aws rds describe-db-instances --db-instance-identifier $de_project"-rds" --output text --query "DBInstances[].DBSubnetGroup.VpcId")

# Install postgreSQL
sudo yum install postgresql15.x86_64 -y

# Install terraform
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo
sudo yum -y install terraform

echo "Terraform has been installed"

# Define Terraform variables
echo "export TF_VAR_project=$de_project" >> $HOME/.bashrc
echo "export TF_VAR_region=$AWS_DEFAULT_REGION" >> $HOME/.bashrc
## Networking
echo "export TF_VAR_vpc_id=$VPC_ID" >> $HOME/.bashrc
echo "export TF_VAR_private_subnet_a_id=$(aws ec2 describe-subnets --filters "Name=tag:aws:cloudformation:logical-id,Values=PrivateSubnetA" "Name=vpc-id,Values=$VPC_ID" --output text --query "Subnets[].SubnetId")" >> $HOME/.bashrc
## Glue ETL
echo "export TF_VAR_db_sg_id=$(aws rds describe-db-instances --db-instance-identifier $de_project-rds --output text --query "DBInstances[].VpcSecurityGroups[].VpcSecurityGroupId")" >> $HOME/.bashrc
echo "export TF_VAR_source_host=$(aws rds describe-db-instances --db-instance-identifier $de_project-rds --output text --query "DBInstances[].Endpoint.Address")" >> $HOME/.bashrc
echo "export TF_VAR_source_port=3306" >> $HOME/.bashrc
echo "export TF_VAR_source_database="classicmodels"" >> $HOME/.bashrc
echo "export TF_VAR_source_username="admin"" >> $HOME/.bashrc
echo "export TF_VAR_source_password="adminpwrd"" >> $HOME/.bashrc
## Vector DB 
echo "export TF_VAR_public_subnet_a_id=$(aws ec2 describe-subnets --filters "Name=tag:aws:cloudformation:logical-id,Values=PublicSubnetA" "Name=vpc-id,Values=$VPC_ID" --output text --query "Subnets[].SubnetId")" >> $HOME/.bashrc
echo "export TF_VAR_public_subnet_b_id=$(aws ec2 describe-subnets --filters "Name=tag:aws:cloudformation:logical-id,Values=PublicSubnetB" "Name=vpc-id,Values=$VPC_ID" --output text --query "Subnets[].SubnetId")" >> $HOME/.bashrc
# Streaming inference
echo "export TF_VAR_kinesis_stream_arn=$(aws kinesis describe-stream --stream-name $de_project-kinesis-data-stream --output text --query "StreamDescription.StreamARN")" >> $HOME/.bashrc
echo "export TF_VAR_inference_api_url=$(aws lambda get-function-url-config --function-name $de_project-model-inference --output text --query "FunctionUrl")" >> $HOME/.bashrc

echo "Terraform variables have been set"

source $HOME/.bashrc

# Replace the bucket name in the backend.tf file
script_dir=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")
sed -i "s/<terraform_state_bucket>/\"$TF_VAR_project-$(aws sts get-caller-identity --query 'Account' --output text)-us-east-1-terraform-state\"/g" "$script_dir/../terraform/backend.tf"
