resource "aws_glue_job" "ratings_transformation_job" {
  name         = "${var.project}-ratings-transformation-job"
  role_arn     = var.glue_role_arn
  glue_version = "4.0"

  command {
    name            = "glueetl"
    script_location = "s3://${data.aws_s3_bucket.scripts.id}/${aws_s3_object.json_glue_job_script.id}"
    python_version  = 3
  }

  default_arguments = {
    "--enable-job-insights" = "true"
    "--job-language"        = "python"
    "--data_lake_bucket"    = data.aws_s3_bucket.data_lake.bucket
    "--database_name"       = var.curated_db_name
    "--ml_table"            = var.curated_db_ml_table
    "--lakehouse_path"      = "s3://${data.aws_s3_bucket.data_lake.bucket}/"
    "--datalake-formats"    = "iceberg"
  }

  timeout = 7

  number_of_workers = 2
  worker_type       = "G.1X"
}

resource "aws_glue_job" "csv_transformation_job" {
  name         = "${var.project}-csv-transformation-job"
  role_arn     = var.glue_role_arn
  glue_version = "4.0"

  command {
    name            = "glueetl"
    script_location = "s3://${data.aws_s3_bucket.scripts.id}/${aws_s3_object.batch_glue_job_script.id}"
    python_version  = 3
  }

  default_arguments = {
    "--enable-job-insights" = "true"
    "--job-language"        = "python"
    "--data_lake_bucket"    = data.aws_s3_bucket.data_lake.bucket
  }

  timeout = 5

  number_of_workers = 2
  worker_type       = "G.1X"
}


resource "aws_glue_job" "ratings_to_iceberg_job" {
  name         = "${var.project}-ratings-to-iceberg-job"
  role_arn     = var.glue_role_arn
  glue_version = "4.0"

  command {
    name            = "glueetl"
    script_location = "s3://${data.aws_s3_bucket.scripts.id}/${aws_s3_object.ratings_to_iceberg_job_script.id}"
    python_version  = 3
  }

  default_arguments = {
    "--enable-job-insights" = "true"
    "--job-language"        = "None"
    "--data_lake_bucket"    = data.aws_s3_bucket.data_lake.bucket
    "--database_name"       = var.curated_db_name
    "--table_name"          = var.curated_db_ratings_table
    "--lakehouse_path"      = "s3://${data.aws_s3_bucket.data_lake.bucket}/"
    "None"                  = "None"
  }

  timeout = None

  number_of_workers = None
  worker_type       = "G.1X"
}
