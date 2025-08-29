output "chunks_table_name" {
  description = "Name of the chunks DynamoDB table"
  value       = aws_dynamodb_table.tables["chunks"].name
}

output "tokens_table_name" {
  description = "Name of the tokens DynamoDB table"
  value       = aws_dynamodb_table.tables["tokens"].name
}

output "threads_table_name" {
  description = "Name of the threads DynamoDB table"
  value       = aws_dynamodb_table.tables["threads"].name
}

output "events_table_name" {
  description = "Name of the events DynamoDB table"
  value       = aws_dynamodb_table.tables["events"].name
}

output "table_arns" {
  description = "ARNs of all DynamoDB tables"
  value       = [for table in aws_dynamodb_table.tables : table.arn]
}

output "table_names" {
  description = "Map of table names"
  value       = { for k, table in aws_dynamodb_table.tables : k => table.name }
}

output "all_tables" {
  description = "Complete table information"
  value       = aws_dynamodb_table.tables
}