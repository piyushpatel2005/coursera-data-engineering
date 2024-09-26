# Adding the Server IP to the Known ssh hosts and avoid Key checking
export server_instance_public_ip=$(aws ec2 describe-instances --filters 'Name=tag:Name,Values=de-c3w1lab1-block-server' --query "Reservations[].Instances[].PublicIpAddress" --output text)
sudo echo -e "Host $server_instance_public_ip\n    StrictHostKeyChecking no\n" > $HOME/.ssh/config

# Getting the server instance id and executing the restart command
export server_instance_id=$(aws ec2 describe-instances --filters 'Name=tag:Name,Values=de-c3w1lab1-block-server' --query "Reservations[].Instances[].InstanceId" --output text)
aws ec2 reboot-instances --instance-ids $server_instance_id
sleep 30
aws ec2 wait instance-running --instance-ids $server_instance_id --region us-east-1
echo "Block server rebooted, try to connect with the client again"