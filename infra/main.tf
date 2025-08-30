module "storage" {
  source = "./modules/storage"
  name   = var.name
}

module "dynamo_db" {
  source                        = "./modules/dynamo_db"
  name                          = var.name
  environment                   = var.environment
  enable_point_in_time_recovery = var.enable_pitr
}

module "compute_lambda" {
  source            = "./modules/compute_lambda"
  name              = var.name
  bucket_name       = module.storage.bucket_name
  ddb_chunks_table  = module.dynamo_db.chunks_table_name
  ddb_tokens_table  = module.dynamo_db.tokens_table_name
  ddb_threads_table = module.dynamo_db.threads_table_name
  ddb_events_table  = module.dynamo_db.events_table_name
  table_arns        = module.dynamo_db.table_arns
  bucket_arn        = module.storage.bucket_arn
}

module "api" {
  source                = "./modules/api"
  name                  = var.name
  lambda_function_arns  = module.compute_lambda.lambda_function_arns
  lambda_function_names = module.compute_lambda.lambda_function_names
}