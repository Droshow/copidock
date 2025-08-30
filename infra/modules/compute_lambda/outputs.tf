output "lambda_functions" {
  description = "Map of all Lambda functions"
  value       = aws_lambda_function.functions
}

output "lambda_function_names" {
  description = "Map of Lambda function names"
  value       = { for k, func in aws_lambda_function.functions : k => func.function_name }
}

output "lambda_function_arns" {
  description = "Map of Lambda function ARNs"
  value       = { for k, func in aws_lambda_function.functions : k => func.arn }
}

# Individual outputs for backward compatibility
output "notes_lambda_arn" {
  description = "ARN of the notes Lambda function"
  value       = aws_lambda_function.functions["notes"].arn
}

output "notes_lambda_function_name" {
  description = "Name of the notes Lambda function"
  value       = aws_lambda_function.functions["notes"].function_name
}

output "thread_start_lambda_arn" {
  description = "ARN of the thread start Lambda function"
  value       = aws_lambda_function.functions["thread_start"].arn
}

output "thread_start_lambda_function_name" {
  description = "Name of the thread start Lambda function"
  value       = aws_lambda_function.functions["thread_start"].function_name
}

output "snapshot_lambda_arn" {
  description = "ARN of the snapshot Lambda function"
  value       = aws_lambda_function.functions["snapshot"].arn
}

output "snapshot_lambda_function_name" {
  description = "Name of the snapshot Lambda function"
  value       = aws_lambda_function.functions["snapshot"].function_name
}

output "rehydrate_lambda_arn" {
  description = "ARN of the rehydrate Lambda function"
  value       = aws_lambda_function.functions["rehydrate"].arn
}

output "rehydrate_lambda_function_name" {
  description = "Name of the rehydrate Lambda function"
  value       = aws_lambda_function.functions["rehydrate"].function_name
}