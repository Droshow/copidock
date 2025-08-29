variable "name" {
  description = "Name prefix for resources"
  type        = string
}

variable "bucket_name" {
  description = "S3 bucket name"
  type        = string
}

variable "bucket_arn" {
  description = "S3 bucket ARN"
  type        = string
}

variable "ddb_chunks_table" {
  description = "DynamoDB chunks table name"
  type        = string
}

variable "ddb_tokens_table" {
  description = "DynamoDB tokens table name"
  type        = string
}

variable "ddb_threads_table" {
  description = "DynamoDB threads table name"
  type        = string
}

variable "ddb_events_table" {
  description = "DynamoDB events table name"
  type        = string
}

variable "table_arns" {
  description = "List of DynamoDB table ARNs"
  type        = list(string)
}