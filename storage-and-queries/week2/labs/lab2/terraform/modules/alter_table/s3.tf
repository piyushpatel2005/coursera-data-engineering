data "aws_s3_bucket" "data_lake" {
  bucket = var.data_lake_name
}

data "aws_s3_bucket" "scripts" {
  bucket = var.scripts_bucket_name
}


resource "aws_s3_object" "alter_table_job_script" {
  bucket = data.aws_s3_bucket.scripts.id
  key    = "de_c3w2a1_alter_ratings_table.py"
  source = "${path.root}/assets/alter_table_job/de_c3w2a1_alter_ratings_table.py"

  etag = filemd5("${path.root}/assets/alter_table_job/de_c3w2a1_alter_ratings_table.py")
}
