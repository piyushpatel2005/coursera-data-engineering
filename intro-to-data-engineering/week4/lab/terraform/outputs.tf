# ETL
output "data_lake_bucket_id" {
  value = module.etl.data_lake_bucket_id
}

output "scripts_bucket_id" {
  value = module.etl.scripts_bucket_id
}

#  Vector-db
output "vector_db_master_username" {
  value     = module.vector_db.vector_db_master_username
  sensitive = true
}

output "vector_db_master_password" {
  value     = module.vector_db.vector_db_master_password
  sensitive = true
}

output "vector_db_host" {
  value = module.vector_db.vector_db_host
}

output "vector_db_port" {
  value = module.vector_db.vector_db_port
}

# Streaming-Inference
output "recommendations_bucket_id" {
  value = module.streaming_inference.recommendations_bucket_id
}
