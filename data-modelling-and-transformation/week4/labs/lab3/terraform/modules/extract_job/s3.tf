data "aws_s3_bucket" "data_lake" {
  bucket = var.data_lake_name
}

resource "aws_s3_bucket" "scripts" {
  bucket        = "${var.project}-${data.aws_caller_identity.current.account_id}-${var.region}-scripts"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "scripts" {
  bucket = aws_s3_bucket.scripts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "glue_job_extract_db" {
  bucket = aws_s3_bucket.scripts.id
  key    = "de-c4w4a2-extract-songs-job.py"
  source = "${path.root}/assets/extract_jobs/de-c4w4a2-extract-songs-job.py"

  etag = filemd5("${path.root}/assets/extract_jobs/de-c4w4a2-extract-songs-job.py")
}

resource "aws_s3_object" "glue_job_extract_api" {
  bucket = aws_s3_bucket.scripts.id
  key    = "de-c4w4a2-api-extract-job.py"
  source = "${path.root}/assets/extract_jobs/de-c4w4a2-api-extract-job.py"

  etag = filemd5("${path.root}/assets/extract_jobs/de-c4w4a2-api-extract-job.py")
}
