#!/bin/bash

# Get the instance ID and its current state
server_instance_id=$(aws ec2 describe-instances \
    --filters 'Name=tag:Name,Values=de-c4w4a1-api-instance' \
    --query "Reservations[].Instances[].InstanceId" --output text)
instance_state=$(aws ec2 describe-instances --instance-ids $server_instance_id \
    --query "Reservations[].Instances[].State.Name" --output text)

# Exit if the instance is terminated
[ "$instance_state" = "terminated" ] && { echo "Instance is terminated, cannot reboot."; exit 1; }

# Reboot the instance and wait for it to be running
aws ec2 reboot-instances --instance-ids $server_instance_id
sleep 80
aws ec2 wait instance-running --instance-ids $server_instance_id --region us-east-1

# Check the final state and output the result
final_state=$(aws ec2 describe-instances --instance-ids $server_instance_id \
    --query "Reservations[].Instances[].State.Name" --output text)

[ "$final_state" = "running" ] && echo "VSCode server rebooted, try to connect again" || \
{ echo "Failed to reboot the instance. Current state: $final_state"; exit 1; }
