output "notes_lambda_arn" {
  description = "ARN of the notes Lambda function"
  value       = aws_lambda_function.notes.arn
}

output "notes_lambda_function_name" {
  description = "Name of the notes Lambda function"
  value       = aws_lambda_function.notes.function_name
}