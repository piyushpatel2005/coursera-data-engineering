output "data_lake_bucket_id" {
  value = data.aws_s3_bucket.data_lake.id
}

output "scripts_bucket_id" {
  value = aws_s3_bucket.scripts.id
}

output "glue_role_arn" {
  value = aws_iam_role.glue_role.arn
}

output "glue_rds_extract_job" {
  value = aws_glue_job.rds_ingestion_etl_job.name
}

output "glue_api_users_extract_job" {
  value = aws_glue_job.api_users_ingestion_etl_job.name
}

output "glue_sessions_users_extract_job" {
  value = aws_glue_job.api_sessions_ingestion_etl_job.name
}

