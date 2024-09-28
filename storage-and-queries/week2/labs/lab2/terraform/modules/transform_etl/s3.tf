data "aws_s3_bucket" "data_lake" {
  bucket = var.data_lake_name
}

data "aws_s3_bucket" "scripts" {
  bucket = var.scripts_bucket_name
}


resource "aws_s3_object" "batch_glue_job_script" {
  bucket = data.aws_s3_bucket.scripts.id
  key    = "de_c3w2a1_batch_transform.py"
  source = "${path.root}/assets/transform_etl_jobs/de_c3w2a1_batch_transform.py"

  etag = filemd5("${path.root}/assets/transform_etl_jobs/de_c3w2a1_batch_transform.py")
}

resource "aws_s3_object" "json_glue_job_script" {
  bucket = data.aws_s3_bucket.scripts.id
  key    = "de_c3w2lab2_json_transform.py"
  source = "${path.root}/assets/transform_etl_jobs/de_c3w2a1_json_transform.py"

  etag = filemd5("${path.root}/assets/transform_etl_jobs/de_c3w2a1_json_transform.py")
}

resource "aws_s3_object" "ratings_to_iceberg_job_script" {
  bucket = data.aws_s3_bucket.scripts.id
  key    = "de_c3w2a1_ratings_to_iceberg.py"
  source = "${path.root}/assets/transform_etl_jobs/de_c3w2a1_ratings_to_iceberg.py"

  etag = filemd5("${path.root}/assets/transform_etl_jobs/de_c3w2a1_ratings_to_iceberg.py")
}

