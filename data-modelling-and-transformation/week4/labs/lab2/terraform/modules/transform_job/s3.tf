# Complete the `bucket` parameter with the value `var.scripts_bucket_name`
data "aws_s3_bucket" "scripts" {
  bucket = var.scripts_bucket_name
}

# Complete the `bucket` parameter with the value `var.data_lake_name`
data "aws_s3_bucket" "data_lake" {
  bucket = var.data_lake_name
}

resource "aws_s3_object" "glue_job_transform_db" {
  # Add the scripts bucket name `data.aws_s3_bucket.scripts.id`
  bucket = data.aws_s3_bucket.scripts.id
  # Add `de-c4w4a1-transform-songs-job.py` as the object key
  key    = "de-c4w4a1-transform-songs-job.py"
  source = "${path.root}/assets/transform_jobs/de-c4w4a1-transform-songs-job.py"

  etag = filemd5("${path.root}/assets/transform_jobs/de-c4w4a1-transform-songs-job.py")
}

resource "aws_s3_object" "glue_job_transform_json" {
  # Add the scripts bucket name `data.aws_s3_bucket.scripts.id`
  bucket = data.aws_s3_bucket.scripts.id
  # Add `de-c4w4a1-transform-json-job.py` as the object key
  key    = "de-c4w4a1-transform-json-job.py"
  source = "${path.root}/assets/transform_jobs/de-c4w4a1-transform-json-job.py"

  etag = filemd5("${path.root}/assets/transform_jobs/de-c4w4a1-transform-json-job.py")
}
