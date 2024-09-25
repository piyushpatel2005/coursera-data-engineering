output "project" {
  value = var.project
}

# Define an output for the public DNS of the EC2
# instance
output "bastion_host_dns" {
  value = module.bastion_host.bastion_host_dns
}

# Define an output for the host of the RDS
output "db_host" {
  value = module.bastion_host.db_host
}

# Define an output for the port of the RDS
output "db_port" {
  value = module.bastion_host.db_port
}

# Define an output for the username of the RDS
output "db_master_username" {
  value = module.bastion_host.db_master_username
}

# Define an output for the master password of the RDS
output "db_master_password" {
  value     = module.bastion_host.db_master_password
  sensitive = true
}
