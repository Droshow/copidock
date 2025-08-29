output "api_url" {
  description = "API Gateway endpoint URL"
  value       = module.api.api_url
}

output "bucket" {
  description = "S3 bucket name"
  value       = module.storage.bucket_name
}

output "dynamodb_tables" {
  description = "DynamoDB table names"
  value = {
    chunks  = module.dynamo_db.chunks_table_name
    tokens  = module.dynamo_db.tokens_table_name
    threads = module.dynamo_db.threads_table_name
    events  = module.dynamo_db.events_table_name
  }
}