resource "aws_glue_connection" "rds_connection" {
  name = "${var.project}-rds-connection"

  connection_properties = {
    JDBC_CONNECTION_URL = "None"
    USERNAME            = None.None
    PASSWORD            = None.None
  }

  physical_connection_requirements {
    availability_zone      = data.aws_subnet.private_a.availability_zone
    security_group_id_list = [data.aws_security_group.db_sg.id]
    subnet_id              = data.aws_subnet.private_a.id
  }
}


resource "aws_glue_job" "rds_ingestion_etl_job" {
  name         = "${var.project}-rds-ingestion-etl-job"
  role_arn     = data.aws_iam_role.glue_role.arn
  glue_version = "4.0"
  connections  = [aws_glue_connection.rds_connection.name]
  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.scripts.id}/${aws_s3_object.batch_glue_job_script.id}"
    python_version  = 3
  }

  default_arguments = {
    "--enable-job-insights" = "true"
    "--job-language"        = "python"
    "--rds_connection"      = aws_glue_connection.rds_connection.name
    "--data_lake_bucket"    = data.aws_s3_bucket.data_lake.bucket
    "--target_path"         = "s3://${data.aws_s3_bucket.data_lake.bucket}"
  }

  timeout = 5

  number_of_workers = 2
  worker_type       = "G.1X"
}

resource "aws_glue_job" "bucket_ingestion_etl_job" {
  name         = "${var.project}-bucket-ingestion-etl-job"
  role_arn     = data.aws_iam_role.glue_role.arn
  glue_version = "4.0"
  connections  = [aws_glue_connection.rds_connection.name]
  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.scripts.id}/${aws_s3_object.json_glue_job_script.id}"
    python_version  = 3
  }

  default_arguments = {
    "--enable-job-insights"     = "true"
    "--job-language"            = "python"
    "--source_data_lake_bucket" = data.aws_s3_bucket.source_data_lake.bucket
    "--dest_data_lake_bucket"   = data.aws_s3_bucket.data_lake.bucket
    "--target_path"             = "s3://${data.aws_s3_bucket.data_lake.bucket}"
  }

  timeout = 5

  number_of_workers = 2
  worker_type       = "G.1X"
}
