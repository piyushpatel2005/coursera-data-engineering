output "glue_ratings_to_iceberg_job" {
  value = aws_glue_job.ratings_to_iceberg_job.name
}

output "glue_csv_transform_job" {
  value = aws_glue_job.csv_transformation_job.name
}

output "glue_ratings_transform_job" {
  value = aws_glue_job.ratings_transformation_job.name
}
