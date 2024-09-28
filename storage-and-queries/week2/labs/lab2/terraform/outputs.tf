output "project" {
  value = var.project
}

# Module: Landing
output "glue_bucket_ingestion_job" {
  value = module.landing_etl.glue_bucket_ingestion_job
}

output "glue_rds_ingestion_job" {
  value = module.landing_etl.glue_rds_ingestion_job
}

# Module: Tranformations
# output "glue_ratings_to_iceberg_job" {
#   value = module.transform_etl.glue_ratings_to_iceberg_job
# }

# output "glue_csv_transform_job" {
#   value = module.transform_etl.glue_csv_transform_job
# }

# output "glue_ratings_transform_job" {
#   value = module.transform_etl.glue_ratings_transform_job
# }

# Module: Alter table
# output "glue_alter_table_job" {
#   value = module.alter_table.glue_alter_table_job
# }
