output "serving_schema" {
  value = redshift_schema.serving_schema.name
}

output "transform_schema" {
  value = redshift_schema.transform_external_from_glue_data_catalog.name
}
