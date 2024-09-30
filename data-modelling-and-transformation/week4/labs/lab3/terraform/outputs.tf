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

output "scripts_bucket" {
  value = module.extract_job.scripts_bucket_id
}

output "data_lake_bucket" {
  value = module.extract_job.data_lake_bucket_id
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


output "sessions_db_ruleset_name" {
  value = module.data_quality.sessions_db_ruleset
}

output "songs_db_ruleset_name" {
  value = module.data_quality.songs_db_ruleset
}

output "users_db_ruleset_name" {
  value = module.data_quality.users_db_ruleset
}
