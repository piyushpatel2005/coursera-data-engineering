resource "aws_glue_connection" "rds_connection" {
  name = "${var.project}-connection-rds"

  connection_properties = {
    JDBC_CONNECTION_URL = "jdbc:postgresql://${var.host}:${var.port}/${var.database}"
    USERNAME            = var.username
    PASSWORD            = var.password
  }

  physical_connection_requirements {
    availability_zone      = data.aws_subnet.private_a.availability_zone
    security_group_id_list = [data.aws_security_group.db_sg.id]
    subnet_id              = data.aws_subnet.private_a.id
  }
}

resource "aws_glue_job" "rds_ingestion_etl_job" {
  name         = "${var.project}-rds-extract-job"
  role_arn     = aws_iam_role.glue_role.arn
  glue_version = "4.0"
  connections  = [aws_glue_connection.rds_connection.name]
  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.scripts.id}/${aws_s3_object.glue_job_extract_db.id}"
    python_version  = 3
  }

  default_arguments = {
    "--enable-job-insights" = "true"
    "--job-language"        = "python"
    "--rds_connection"      = aws_glue_connection.rds_connection.name
    "--data_lake_bucket"    = data.aws_s3_bucket.data_lake.bucket
    "--ingest_date"         = "2020-02-01"
  }

  timeout = 5

  number_of_workers = 2
  worker_type       = "G.1X"
}

resource "aws_glue_job" "api_users_ingestion_etl_job" {
  name         = "${var.project}-api-users-extract-job"
  role_arn     = aws_iam_role.glue_role.arn
  glue_version = "4.0"

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.scripts.id}/${aws_s3_object.glue_job_extract_api.id}"
    python_version  = 3
  }

  default_arguments = {
    "--enable-job-insights" = "true"
    "--job-language"        = "python"
    "--api_start_date"      = "2020-01-01"
    "--api_end_date"        = "2020-01-31"
    "--ingest_date"         = "2020-02-01"
    "--api_url"             = "http://34.206.194.53:8000/users"
    "--target_path"         = "s3://${data.aws_s3_bucket.data_lake.bucket}/landing_zone/api/users"
  }

  timeout = 5

  number_of_workers = 2
  worker_type       = "G.1X"
}

resource "aws_glue_job" "api_sessions_ingestion_etl_job" {
  name         = "${var.project}-api-sessions-extract-job"
  role_arn     = aws_iam_role.glue_role.arn
  glue_version = "4.0"
  #connections  = [aws_glue_connection.rds_connection.name]
  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.scripts.id}/${aws_s3_object.glue_job_extract_api.id}"
    python_version  = 3
  }

  default_arguments = {
    "--enable-job-insights" = "true"
    "--job-language"        = "python"
    "--api_start_date"      = "2020-01-01"
    "--api_end_date"        = "2020-01-31"
    "--ingest_date"         = "2020-02-01"
    "--api_url"             = "http://34.206.194.53:8000/sessions"
    "--target_path"         = "s3://${data.aws_s3_bucket.data_lake.bucket}/landing_zone/api/sessions"
  }

  timeout = 5

  number_of_workers = 2
  worker_type       = "G.1X"
}
