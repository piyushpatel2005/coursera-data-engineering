# Adding the Airflow IP to the Known ssh hosts and avoid Key checking
export airflow_instance_public_ip=$(aws ec2 describe-instances --filters 'Name=tag:Name,Values=de-c2w4lab2-airflow-instance' --query "Reservations[].Instances[].PublicIpAddress" --output text)
sudo echo -e "Host $airflow_instance_public_ip\n    StrictHostKeyChecking no\n" > $HOME/.ssh/config

# Getting the airflow instance id and executing the restart airflow services script
export airflow_instance_id=$(aws ec2 describe-instances --filters 'Name=tag:Name,Values=de-c2w4lab2-airflow-instance' --query "Reservations[].Instances[].InstanceId" --output text)
echo "sudo bash /opt/airflow/restart_airflow.sh" | aws ec2-instance-connect ssh --instance-id $airflow_instance_id 2> $PWD/scripts/restart_airflow_err.log  1> $PWD/scripts/restart_airflow_output.log &
pid_restart=$!  # Get the PID of the background process
wait $pid_restart  # Wait for the background process to finish


# Checking the availability of the services
while true; do
    echo "Checking the status of the services..."
    echo "sudo docker ps|grep airflow-webserver" | aws ec2-instance-connect ssh --instance-id $airflow_instance_id 2> $PWD/scripts/health_check_err.log 1> $PWD/scripts/health_check_output.log &
    pid=$!  # Get the PID of the background process
    wait $pid  # Wait for the background process to finish
    
    #grep -o 'airflow-webserver' $PWD/scripts/health_check_output.log
    
    output=$(grep -o 'healthy' $PWD/scripts/health_check_output.log)

    if [[ -n $output ]]; then
        echo "Service is healthy!"
        break
    else
        echo "Service is not healthy yet. Waiting 30 seconds..."
        sleep 30
        rm $PWD/scripts/health_check_*.log
    fi
done

# Removing logs
rm $PWD/scripts/restart_airflow_*.log
rm $PWD/scripts/health_check_*.log
