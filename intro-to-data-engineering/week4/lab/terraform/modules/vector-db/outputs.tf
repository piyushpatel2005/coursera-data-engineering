output "vector_db_master_username" {
  value     = var.master_username
  sensitive = true
}

output "vector_db_master_password" {
  value     = random_id.master_password.id
  sensitive = true
}

output "vector_db_host" {
  value = aws_db_instance.master_db.address
}

output "vector_db_port" {
  value = aws_db_instance.master_db.port
}
