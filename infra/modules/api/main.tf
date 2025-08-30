locals {
  api_routes = {
    post_notes = {
      route_key   = "POST /notes"
      lambda_key  = "notes"
      description = "Create and store notes"
    }
    get_notes = {
      route_key   = "GET /notes"
      lambda_key  = "notes"
      description = "Retrieve stored notes"
    }
    post_thread_start = {
      route_key   = "POST /thread/start"
      lambda_key  = "thread_start"
      description = "Start a new decision thread"
    }
    post_snapshot = {
      route_key   = "POST /snapshot"
      lambda_key  = "snapshot"
      description = "Create thread context snapshot"
    }
    get_rehydrate = {
      route_key   = "GET /rehydrate/{thread}/latest"
      lambda_key  = "rehydrate"
      description = "Get latest thread snapshot"
    }
  }
}

resource "aws_apigatewayv2_api" "http" {
  name          = "${var.name}-api"
  protocol_type = "HTTP"
  description   = "Copidock serverless API for note management and thread rehydration"

  cors_configuration {
    allow_credentials = false
    allow_headers     = ["content-type", "x-amz-date", "authorization", "x-api-key"]
    allow_methods     = ["*"]
    allow_origins     = ["*"]
    expose_headers    = ["date", "keep-alive"]
    max_age           = 86400
  }

  tags = {
    Name = "${var.name}-api"
  }
}

# Integrations
resource "aws_apigatewayv2_integration" "lambda_integrations" {
  for_each = toset(distinct([for route in local.api_routes : route.lambda_key]))

  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = var.lambda_function_arns[each.value]
  payload_format_version = "2.0"
  description            = "Integration for ${each.value} Lambda function"
}

# Routes
resource "aws_apigatewayv2_route" "routes" {
  for_each = local.api_routes

  api_id    = aws_apigatewayv2_api.http.id
  route_key = each.value.route_key
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integrations[each.value.lambda_key].id}"

  # Optional: Enable API key requirement
  # api_key_required = true
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http.id
  name        = "$default"
  auto_deploy = true
  description = "Default stage for Copidock API"

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_logs.arn
    format = jsonencode({
      requestId        = "$context.requestId"
      ip               = "$context.identity.sourceIp"
      requestTime      = "$context.requestTime"
      httpMethod       = "$context.httpMethod"
      routeKey         = "$context.routeKey"
      status           = "$context.status"
      protocol         = "$context.protocol"
      responseLength   = "$context.responseLength"
      error            = "$context.error.message"
      integrationError = "$context.integration.error"
    })
  }

  tags = {
    Name = "${var.name}-api-stage"
  }
}

# CloudWatch Log Group for API Gateway
resource "aws_cloudwatch_log_group" "api_logs" {
  name              = "/aws/apigateway/${var.name}-api"
  retention_in_days = 30

  tags = {
    Name = "${var.name}-api-logs"
  }
}

# Lambda permissions
resource "aws_lambda_permission" "api_lambda_permissions" {
  for_each = var.lambda_function_names

  statement_id  = "AllowExecutionFromAPIGateway-${each.key}"
  action        = "lambda:InvokeFunction"
  function_name = each.value
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}