resource "redshift_schema" "serving_schema" {
  name  = "deftunes_serving"
  owner = var.redshift_user
  quota = 50
}


# External schema using AWS Glue Data Catalog
resource "redshift_schema" "transform_external_from_glue_data_catalog" {
  name  = "deftunes_transform"
  owner = var.redshift_user
  external_schema {
    database_name = var.catalog_database
    data_catalog_source {
      iam_role_arns = [
        data.aws_iam_role.redshift_spectrum_role.arn
      ]
      create_external_database_if_not_exists = true
    }
  }
}
