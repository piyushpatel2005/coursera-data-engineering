resource "aws_glue_catalog_database" "transform_db" {
  name        = var.catalog_database
  description = "Glue Catalog database for transformations"
}

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
    "--catalog_database"        = aws_glue_catalog_database.transform_db.name
    "--ingest_date"             = "2020-02-01"
    "--users_source_path"       = "s3://${data.aws_s3_bucket.data_lake.id}/landing_zone/api/users/"
    "--sessions_source_path"    = "s3://${data.aws_s3_bucket.data_lake.id}/landing_zone/api/sessions/"
    "--target_bucket_path"      = "${data.aws_s3_bucket.data_lake.id}"
    "--users_table"             = var.users_table
    "--sessions_table"          = var.sessions_table
    "--datalake-formats"        = "iceberg"
    "--enable-glue-datacatalog" = true

  }

  timeout = 5

  number_of_workers = 2
  worker_type       = "G.1X"
}

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
    "--ingest_date"             = "2020-02-01"
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
