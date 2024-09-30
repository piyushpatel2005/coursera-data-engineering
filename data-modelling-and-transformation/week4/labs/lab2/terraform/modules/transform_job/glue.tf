# For the `"aws_glue_catalog_database" "transform_db"` resource, set the name to `var.catalog_database`
resource "aws_glue_catalog_database" "transform_db" {
  name        = var.catalog_database
  description = "Glue Catalog database for transformations"
}


# For the resource `"aws_glue_job" "json_transformation_job"` add parameters to the `default_arguments` configuration
resource "aws_glue_job" "json_transformation_job" {
  name         = "${var.project}-json-transform-job"
  role_arn     = var.glue_role_arn
  glue_version = "4.0"
  command {
    name            = "glueetl"
    script_location = "s3://${data.aws_s3_bucket.scripts.id}/${aws_s3_object.glue_job_transform_json.id}"
    python_version  = 3
  }

  default_arguments = {
    "--enable-job-insights"     = "true"
    "--job-language"            = "python"
    # Set `"--catalog_database"` to `aws_glue_catalog_database.transform_db.name`
    "--catalog_database"        = aws_glue_catalog_database.transform_db.name
    # Set `"--ingest_date"` to your ingestion date which should be your current date in the format: `"yyyy-mm-dd"` 
    # (replace the placeholder `<YOUR-CURRENT-DATE>`)
    "--ingest_date"             = "2024-09-30"
    # Review the users source path
    "--users_source_path"       = "s3://${data.aws_s3_bucket.data_lake.id}/landing_zone/api/users/"
    # Review the sessions source path
    "--sessions_source_path"    = "s3://${data.aws_s3_bucket.data_lake.id}/landing_zone/api/sessions/"
    # Review the target bucket path
    "--target_bucket_path"      = "${data.aws_s3_bucket.data_lake.id}"
    # Set `"--users_table"` to `var.users_table`
    "--users_table"             = var.users_table
    # Set `"--sessions_table"` to `var.sessions_table`
    "--sessions_table"          = var.sessions_table
    # Set `"--datalake-formats"` to `"iceberg"`
    "--datalake-formats"        = "iceberg"
    "--enable-glue-datacatalog" = true

  }

  timeout = 5

  number_of_workers = 2
  worker_type       = "G.1X"
}

# Review the default arguments configuration in the `"aws_glue_job" "json_transformation_job"` resource
resource "aws_glue_job" "songs_transformation_job" {
  name         = "${var.project}-songs-transform-job"
  role_arn     = var.glue_role_arn
  glue_version = "4.0"

  command {
    name            = "glueetl"
    script_location = "s3://${data.aws_s3_bucket.scripts.id}/${aws_s3_object.glue_job_transform_db.id}"
    python_version  = 3
  }

  default_arguments = {
    "--enable-job-insights"     = "true"
    "--job-language"            = "python"
    "--catalog_database"        = aws_glue_catalog_database.transform_db.name
    # Set `"--ingest_date"` to your ingestion date which should be your current date in the format: `"yyyy-mm-dd"` 
    # (replace the placeholder `<YOUR-CURRENT-DATE>`)
    "--ingest_date"             = "2024-09-30"
    "--source_bucket_path"      = "${data.aws_s3_bucket.data_lake.id}"
    "--target_bucket_path"      = "${data.aws_s3_bucket.data_lake.id}"
    "--songs_table"             = var.songs_table
    "--datalake-formats"        = "iceberg"
    "--enable-glue-datacatalog" = true

  }

  timeout = 5

  number_of_workers = 2
  worker_type       = "G.1X"
}
