output "glue_json_transformation_job" {
  value = aws_glue_job.json_transformation_job.name
}

output "glue_songs_transformation_job" {
  value = aws_glue_job.songs_transformation_job.name
}

output "glue_catalog_db" {
  value = aws_glue_catalog_database.transform_db.name
}
