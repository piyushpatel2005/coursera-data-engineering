# Complete the `data "aws_s3_bucket" "data_lake"` resource by setting the `bucket` parameter to `var.data_lake_name`
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

# In the resource `"aws_s3_object" "glue_job_extract_db"`, set the `bucket` to the scripts bucket with `aws_s3_bucket.scripts.id`
# Then, add the RDS extraction job name `"de-c4w4a1-extract-songs-job.py"` as the value for the `key` parameter
resource "aws_s3_object" "glue_job_extract_db" {
  bucket = aws_s3_bucket.scripts.id
  key    = "de-c4w4a1-extract-songs-job.py"
  source = "${path.root}/assets/extract_jobs/de-c4w4a1-extract-songs-job.py"

  etag = filemd5("${path.root}/assets/extract_jobs/de-c4w4a1-extract-songs-job.py")
}

# For the resource `"aws_s3_object" "glue_job_extract_api"` also add the same scripts bucket for the `bucket` parameter
# Set the value `"de-c4w4a1-api-extract-job.py"` for the script object key
resource "aws_s3_object" "glue_job_extract_api" {
  bucket = aws_s3_bucket.scripts.id
  key    = "de-c4w4a1-api-extract-job.py"
  source = "${path.root}/assets/extract_jobs/de-c4w4a1-api-extract-job.py"

  etag = filemd5("${path.root}/assets/extract_jobs/de-c4w4a1-api-extract-job.py")
}
