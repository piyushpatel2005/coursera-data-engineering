resource "aws_s3_bucket" "data_lake" {
  bucket_prefix = "${var.project}-datalake-${data.aws_caller_identity.current.account_id}-"
}

resource "aws_s3_bucket_public_access_block" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "scripts" {
  bucket_prefix = "${var.project}-scripts-${data.aws_caller_identity.current.account_id}-"
}

resource "aws_s3_bucket_public_access_block" "scripts" {
  bucket = aws_s3_bucket.scripts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "glue_job_script" {
  bucket = aws_s3_bucket.scripts.id
  key    = "glue_job.py"
  source = "./assets/glue_job.py"

  etag = filemd5("./assets/glue_job.py")
}
