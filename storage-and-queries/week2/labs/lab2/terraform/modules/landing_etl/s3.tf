data "aws_caller_identity" "current" {}
data "aws_s3_bucket" "data_lake" {
  bucket = var.data_lake_name
}

data "aws_s3_bucket" "source_data_lake" {
  bucket = var.source_data_lake_name
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

resource "aws_s3_object" "batch_glue_job_script" {
  bucket = aws_s3_bucket.scripts.id
  key    = "de_c3w2a1_batch_ingress.py"
  source = "${path.root}/assets/landing_etl_jobs/de_c3w2a1_batch_ingress.py"

  etag = filemd5("${path.root}/assets/landing_etl_jobs/de_c3w2a1_batch_ingress.py")
}

resource "aws_s3_object" "json_glue_job_script" {
  bucket = aws_s3_bucket.scripts.id
  key    = "de_c3w2a1_json_ingress.py"
  source = "${path.root}/assets/landing_etl_jobs/de_c3w2a1_json_ingress.py"

  etag = filemd5("${path.root}/assets/landing_etl_jobs/de_c3w2a1_json_ingress.py")
}
