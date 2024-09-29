#!/bin/bash
set -e
export de_project="de-c4w1a1"
export docker_image="public.ecr.aws/deeplearning-ai/dlai-de-c4w1a1-jupyter-env:latest"
export de_project_underscore=$(echo $de_project|sed -r 's/[-]+/_/g')
export AWS_DEFAULT_REGION="us-east-1"
REQUIREMENTS_FILE="$(pwd)/scripts/requirements.txt"
export instance_public_ip=$(ec2-metadata --public-ip|grep -oE '[0-9]+(\.[0-9]+)+')
export instance_id=$(aws ec2 describe-instances --query "Reservations[].Instances[?PublicIpAddress=='$instance_public_ip'].InstanceId" --output text)
export VPC_ID=$(aws ec2 describe-vpcs --filter Name=tag:Name,Values=$de_project --query Vpcs[].VpcId --output text)

# Getting instance_id and corresponding security_group_id
export security_group_id=$(aws ec2 describe-instances --output table --query 'Reservations[*].Instances[*].NetworkInterfaces[*].Groups[*].GroupId' --region $AWS_DEFAULT_REGION --instance-ids $instance_id --output text)

# ## Adding ingress rule to pot 8888 and all sources
export sg_modification_status=$(aws ec2 authorize-security-group-ingress --group-id $security_group_id --protocol tcp --port 8888 --cidr 0.0.0.0/0 --query 'Return' --output text)
echo "Security group modified properly: $sg_modification_status"

sudo yum install postgresql15.x86_64 -y
sudo yum install libpq-devel -y


## Installing docker 
sudo yum update -y 
sudo yum install docker -y 
sudo service docker start 
sudo usermod -a -G docker $USER 
docker pull $docker_image
docker run -d -it -v $(pwd)/scripts/profiles.yml:/app/scripts/profiles.yml -v $(pwd)/images/:/app/images/ -v $(pwd)/C4_W1_Assignment.ipynb:/app/C4_W1_Assignment.ipynb -p 8888:8888 -p 5432:5432 $docker_image

echo "Jupyter lab deployed"

sleep 25

## Getting container ID to extract logs
CONTAINER_ID=$(docker ps -a --filter "ancestor=$docker_image" --format "{{.ID}}")

echo "Container id $CONTAINER_ID"

## Extract the URL from the output file
jupyter_url_local=$(docker logs $CONTAINER_ID|grep -oP 'http://127.0.0.1:\d+/lab\?token=[a-f0-9]+' | head -1)

echo "jupyter url local $jupyter_url_local"

## Get the EC2 instance's public DNS name
ec2_dns=$(ec2-metadata --public-hostname|grep -o ec2-.*)

## Replace the DNS in the URL
jupyter_url=$(echo "$jupyter_url_local" | sed "s/127.0.0.1/${ec2_dns}/")

## Install Jupyter Lab
python3 -m venv lab-venv
source lab-venv/bin/activate
pip install --upgrade pip
pip install -r "$REQUIREMENTS_FILE"

echo "Requirements installed successfully"

# Print the updated URL
echo "Jupyter is running at: $jupyter_url" >> jupyter_output.log
echo "Jupyter is running at: $jupyter_url"
