module "landing_etl" {
  source = "./modules/landing_etl"

  project               = var.project
  region                = var.region
  private_subnet_a_id   = var.private_subnet_a_id
  db_sg_id              = var.db_sg_id
  host                  = var.source_host
  port                  = var.source_port
  database              = var.source_database
  username              = var.source_username
  password              = var.source_password
  source_data_lake_name = var.source_data_lake_name
  data_lake_name        = var.data_lake_name
  glue_role_name        = var.glue_role_name
}

# module "transform_etl" {
#   source = "./modules/transform_etl"

#   project                  = var.project
#   region                   = var.region
#   private_subnet_a_id      = var.private_subnet_a_id
#   glue_role_arn            = module.landing_etl.glue_role_arn
#   data_lake_name           = var.data_lake_name
#   curated_db_name          = var.curated_db_name
#   curated_db_ratings_table = var.curated_db_ratings_table
#   curated_db_ml_table      = var.curated_db_ml_table
#   scripts_bucket_name      = module.landing_etl.scripts_bucket_id

#   depends_on = [module.landing_etl]
# }

# module "alter_table" {
#   source = "./modules/alter_table"

#   project                  = var.project
#   region                   = var.region
#   glue_role_arn            = module.landing_etl.glue_role_arn
#   data_lake_name           = var.data_lake_name
#   curated_db_name          = var.curated_db_name
#   curated_db_ratings_table = var.curated_db_ratings_table
#   scripts_bucket_name      = module.landing_etl.scripts_bucket_id
#   ratings_new_column_name  = var.ratings_new_column_name
#   ratings_new_column_type  = var.ratings_new_column_type


#   depends_on = [module.landing_etl, module.transform_etl]
# }
