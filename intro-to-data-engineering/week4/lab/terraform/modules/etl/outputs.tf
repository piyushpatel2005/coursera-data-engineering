output "data_lake_bucket_id" {
  value = aws_s3_bucket.data_lake.id
}

output "scripts_bucket_id" {
  value = aws_s3_bucket.scripts.id
}
