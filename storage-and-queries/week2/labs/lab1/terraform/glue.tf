resource "aws_glue_job" "reviews_etl_job" {
  name         = "${var.project}-reviews-etl-job"
  role_arn     = aws_iam_role.glue_role.arn
  glue_version = "4.0"

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.scripts.id}/${aws_s3_object.glue_job_reviews_script.id}"
    python_version  = 3
  }

  default_arguments = {
    "--enable-job-insights" = "true"
    "--job-language"        = "python"
    "--conf"                = "spark.rpc.message.maxSize=2000"
    "--enable-metrics"      = "true"
    "--s3_bucket"           = data.aws_s3_bucket.data_lake.bucket
    "--source_path"         = "staging/reviews_Toys_and_Games.json.gz"
    "--target_path"         = "toys_reviews/"
    "--compression"         = "snappy"
    "--partition_cols"      = jsonencode(["year", "month"])
  }

  timeout = 15

  number_of_workers = 2
  worker_type       = "G.1X"
}

resource "aws_glue_job" "metadata_etl_job" {
  name         = "${var.project}-metadata-etl-job"
  role_arn     = aws_iam_role.glue_role.arn
  glue_version = "4.0"

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.scripts.id}/${aws_s3_object.glue_job_metadata_script.id}"
    python_version  = 3

  }

  default_arguments = {
    "--enable-job-insights"       = "true"
    "--job-language"              = "python"
    "--additional-python-modules" = "smart_open==7.0.4"
    "--conf"                      = "spark.rpc.message.maxSize=2000"
    "--enable-metrics"            = "true"
    "--s3_bucket"                 = data.aws_s3_bucket.data_lake.bucket
    "--source_path"               = "staging/meta_Toys_and_Games.json.gz"
    "--target_path"               = "toys_metadata/"
    "--compression"               = "snappy"
    "--partition_cols"            = jsonencode(["sales_category"])
  }

  timeout = 10

  number_of_workers = 2
  worker_type       = "G.1X"
}
