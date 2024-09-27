data "aws_s3_bucket" "data_lake" {
  bucket = var.data_lake_name
}

resource "aws_s3_bucket" "scripts" {
  bucket_prefix = "${var.project}-${data.aws_caller_identity.current.account_id}-scripts"
}

resource "aws_s3_bucket_public_access_block" "scripts" {
  bucket = aws_s3_bucket.scripts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "glue_job_reviews_script" {
  bucket = aws_s3_bucket.scripts.id
  key    = "de-c3w2-reviews-transform-job.py"
  source = "./assets/de-c3w2-reviews-transform-job.py"

  etag = filemd5("./assets/de-c3w2-reviews-transform-job.py")
}


resource "aws_s3_object" "glue_job_metadata_script" {
  bucket = aws_s3_bucket.scripts.id
  key    = "de-c3w2-metadata-transform-job.py"
  source = "./assets/de-c3w2-metadata-transform-job.py"

  etag = filemd5("./assets/de-c3w2-metadata-transform-job.py")
}
