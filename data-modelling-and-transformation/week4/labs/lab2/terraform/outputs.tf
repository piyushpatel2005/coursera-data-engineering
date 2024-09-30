output "project" {
  value = var.project
}

# Module: Extract
output "glue_rds_extract_job" {
  value = module.extract_job.glue_rds_extract_job
}

output "glue_api_users_extract_job" {
  value = module.extract_job.glue_api_users_extract_job
}

output "glue_sessions_users_extract_job" {
  value = module.extract_job.glue_sessions_users_extract_job
}

output "glue_role_arn" {
  value = module.extract_job.glue_role_arn
}

# Transform module
output "glue_catalog_db" {
  value     = module.transform_job.glue_catalog_db
  sensitive = true
}

output "glue_json_transformation_job" {
  value = module.transform_job.glue_json_transformation_job
}

output "glue_songs_transformation_job" {
  value = module.transform_job.glue_songs_transformation_job
}


# Serving module
output "serving_schema" {
  value = module.serving.serving_schema
}

output "transform_schema" {
  value = module.serving.transform_schema
}
