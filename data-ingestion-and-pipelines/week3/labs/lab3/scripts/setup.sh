#!/bin/bash
set -e
export de_project="de-c2w3lab2"
export AWS_DEFAULT_REGION="us-east-1"
export VPC_ID=$(aws ec2 describe-vpcs --filter Name=tag:Name,Values=$de_project --query Vpcs[].VpcId --output text)

sudo yum -y update  
sudo yum -y install postgresql15.x86_64
sudo yum -y install yum-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo
sudo yum -y install terraform

sudo yum -y install make automake libtool pkgconfig libaio-devel
# For MySQL support, replace with mysql-devel on RHEL/CentOS 5
sudo yum -y install openssl-devel
# For PostgreSQL support
sudo yum -y install postgresql-devel


echo "Terraform has been installed"

echo "export TF_VAR_project=$de_project" >> $HOME/.bashrc
echo "export TF_VAR_region=$AWS_DEFAULT_REGION" >> $HOME/.bashrc
echo "export TF_VAR_vpc_id=$VPC_ID" >> $HOME/.bashrc
echo "export TF_VAR_public_subnet_a_id=$(aws ec2 describe-subnets --filters "Name=tag:aws:cloudformation:logical-id,Values=PublicSubnetA" "Name=vpc-id,Values=$VPC_ID" --output text --query "Subnets[].SubnetId")" >> $HOME/.bashrc
echo "export TF_VAR_public_subnet_b_id=$(aws ec2 describe-subnets --filters "Name=tag:aws:cloudformation:logical-id,Values=PublicSubnetB" "Name=vpc-id,Values=$VPC_ID" --output text --query "Subnets[].SubnetId")" >> $HOME/.bashrc
echo "export TF_VAR_private_subnet_a_id=$(aws ec2 describe-subnets --filters "Name=tag:aws:cloudformation:logical-id,Values=PrivateSubnetA" "Name=vpc-id,Values=$VPC_ID" --output text --query "Subnets[].SubnetId")" >> $HOME/.bashrc
echo "export TF_VAR_private_subnet_b_id=$(aws ec2 describe-subnets --filters "Name=tag:aws:cloudformation:logical-id,Values=PrivateSubnetB" "Name=vpc-id,Values=$VPC_ID" --output text --query "Subnets[].SubnetId")" >> $HOME/.bashrc
source $HOME/.bashrc

# Replace the bucket name in the backend.tf file
script_dir=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")
sed -i "s/<terraform_state_bucket>/\"$de_project-$(aws sts get-caller-identity --query 'Account' --output text)-$AWS_DEFAULT_REGION-terraform-state\"/g" "$script_dir/../terraform/backend.tf"
