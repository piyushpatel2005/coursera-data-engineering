data "aws_s3_bucket" "scripts" {
  bucket = var.scripts_bucket_name
}

data "aws_s3_bucket" "data_lake" {
  bucket = var.data_lake_name
}


resource "aws_s3_object" "glue_job_transform_db" {
  bucket = data.aws_s3_bucket.scripts.id
  key    = "de-c4w4a2-transform-songs-job.py"
  source = "${path.root}/assets/transform_jobs/de-c4w4a2-transform-songs-job.py"

  etag = filemd5("${path.root}/assets/transform_jobs/de-c4w4a2-transform-songs-job.py")
}

resource "aws_s3_object" "glue_job_transform_json" {
  bucket = data.aws_s3_bucket.scripts.id
  key    = "de-c4w4a2-transform-json-job.py"
  source = "${path.root}/assets/transform_jobs/de-c4w4a2-transform-json-job.py"

  etag = filemd5("${path.root}/assets/transform_jobs/de-c4w4a2-transform-json-job.py")
}
