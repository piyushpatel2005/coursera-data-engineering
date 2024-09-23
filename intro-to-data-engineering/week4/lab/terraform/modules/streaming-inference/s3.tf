resource "aws_s3_bucket" "recommendations" {
  bucket        = "${var.project}-${data.aws_caller_identity.current.account_id}-${var.region}-recommendations"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "recommendations" {
  bucket = aws_s3_bucket.recommendations.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
