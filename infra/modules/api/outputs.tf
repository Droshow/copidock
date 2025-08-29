output "api_url" {
  description = "API Gateway endpoint URL"
  value       = aws_apigatewayv2_api.http.api_endpoint
}

output "api_id" {
  description = "API Gateway ID"
  value       = aws_apigatewayv2_api.http.id
}