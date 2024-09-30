#!/bin/bash
set -e
export de_project="de-c4w4a2"
export de_project_underscore=$(echo "$de_project" | sed 's/-/_/g')
export AWS_DEFAULT_REGION="us-east-1"
export VPC_ID=$(aws rds describe-db-instances --db-instance-identifier $de_project-rds --output text --query "DBInstances[].DBSubnetGroup.VpcId")

REQUIREMENTS_FILE="$(pwd)/scripts/requirements.txt"

# Installing terraform and Postgres
sudo apt update && sudo apt upgrade -y
sudo apt-get install libpq-dev -y
sudo apt-get install postgresql -y
sudo apt-get install zip -y

echo " Postgres have been installed"

# Define Terraform variables
echo "export TF_VAR_project=$de_project" >> $HOME/.bashrc
echo "export TF_VAR_region=$AWS_DEFAULT_REGION" >> $HOME/.bashrc
echo "export TF_VAR_vpc_id=$VPC_ID" >> $HOME/.bashrc
echo "export TF_VAR_private_subnet_a_id=$(aws ec2 describe-subnets --filters "Name=tag:aws:cloudformation:logical-id,Values=PrivateSubnetA" "Name=vpc-id,Values=$VPC_ID" --output text --query "Subnets[].SubnetId")" >> $HOME/.bashrc
echo "export TF_VAR_db_sg_id=$(aws rds describe-db-instances --db-instance-identifier $de_project-rds --output text --query "DBInstances[].VpcSecurityGroups[].VpcSecurityGroupId")" >> $HOME/.bashrc
echo "export TF_VAR_source_host=$(aws rds describe-db-instances --db-instance-identifier $de_project-rds --output text --query "DBInstances[].Endpoint.Address")" >> $HOME/.bashrc
echo "export TF_VAR_source_port=5432" >> $HOME/.bashrc
echo "export TF_VAR_source_database="postgres"" >> $HOME/.bashrc
echo "export TF_VAR_source_username="postgresuser"" >> $HOME/.bashrc
echo "export TF_VAR_source_password="adminpwrd"" >> $HOME/.bashrc
echo "export TF_VAR_data_lake_name=$(aws s3api list-buckets --query 'Buckets[?starts_with(Name, `'"$de_project"'`) && ends_with(Name, `data-lake`)].Name' --output text)" >> $HOME/.bashrc
echo "export TF_VAR_catalog_database="${de_project_underscore}_transform_db"" >> $HOME/.bashrc
echo "export TF_VAR_users_table="users"" >> $HOME/.bashrc
echo "export TF_VAR_sessions_table="sessions"" >> $HOME/.bashrc
echo "export TF_VAR_songs_table="songs"" >> $HOME/.bashrc
echo "export TF_VAR_redshift_role_name="$de_project-load-role"" >> $HOME/.bashrc
echo "export TF_VAR_redshift_host=$(aws redshift describe-clusters --cluster-identifier $de_project-redshift-cluster --query "Clusters[0].Endpoint.Address" --output text)" >> $HOME/.bashrc
echo "export TF_VAR_redshift_user="defaultuser"" >> $HOME/.bashrc
echo "export TF_VAR_redshift_password="Defaultuserpwrd1234+"" >> $HOME/.bashrc
echo "export TF_VAR_redshift_database="dev"" >> $HOME/.bashrc
echo "export TF_VAR_redshift_port=5439" >> $HOME/.bashrc

source $HOME/.bashrc

# Replace the bucket name in the backend.tf file
script_dir=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")
sed -i "s/<terraform_state_bucket>/\"$de_project-$(aws sts get-caller-identity --query 'Account' --output text)-us-east-1-terraform-state\"/g" "$script_dir/../terraform/backend.tf"

## Install Jupyter Lab
python3 -m venv jupyterlab-venv
source jupyterlab-venv/bin/activate
pip install --upgrade pip
pip install -r "$REQUIREMENTS_FILE"

echo "Requirements installed successfully"

## Run Jupyter Lab in the background and redirect output to a file
nohup jupyter lab --ip 0.0.0.0 --port 8888 > jupyter_output.log 2>&1 &

## Wait for a moment to ensure Jupyter Lab starts
sleep 15

## Extract the URL from the output file
jupyter_url_local=$(grep -oP 'http://127.0.0.1:\d+/lab\?token=[a-f0-9]+' jupyter_output.log | head -1)

## Get the EC2 instance's public DNS name
ec2_dns=$(curl https://ipinfo.io/ip)

## Replace the DNS in the URL
jupyter_url=$(echo "$jupyter_url_local" | sed "s/127.0.0.1/${ec2_dns}/")

# Print the updated URL
echo "Jupyter is running at: $jupyter_url" >> jupyter_output.log
echo "Jupyter is running at: $jupyter_url"