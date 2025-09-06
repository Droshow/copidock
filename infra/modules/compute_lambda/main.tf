locals {
  lambda_functions = {
    notes = {
      handler     = "notes_handler.handler"
      timeout     = 10
      description = "Handle notes operations"
    }
    thread_start = {
      handler     = "thread_start_handler.handler"
      timeout     = 10
      description = "Start new decision threads"
    }
    snapshot = {
      handler     = "snapshot_handler.handler"
      timeout     = 30
      description = "Create snapshots of thread context"
    }
    rehydrate = {
      handler     = "rehydrate_handler.handler"
      timeout     = 10
      description = "Rehydrate thread context from snapshots"
    }
  }
}

resource "aws_iam_role" "lambda_role" {
  name = "${var.name}-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "lambda_inline" {
  statement {
    actions   = ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"]
    resources = ["${var.bucket_arn}/*"]
  }

  statement {
    actions   = ["s3:ListBucket", "s3:GetBucketLocation"]
    resources = [var.bucket_arn]
  }

  statement {
    actions = [
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
      "dynamodb:Query",
      "dynamodb:BatchWriteItem",
      "dynamodb:Scan"
    ]
    resources = var.table_arns
  }

  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_role_policy" "lambda_inline" {
  role   = aws_iam_role.lambda_role.id
  policy = data.aws_iam_policy_document.lambda_inline.json
}

# Create archive files for each Lambda function
data "archive_file" "lambda_zip" {
  for_each = local.lambda_functions

  type        = "zip"
  output_path = "${path.module}/${each.key}_lambda.zip"

  source_dir = "${path.root}/../lambdas"
  excludes   = ["__pycache__", "*.pyc"]
}

# Lambda functions
resource "aws_lambda_function" "functions" {
  for_each = local.lambda_functions

  function_name    = "${var.name}-${each.key}"
  role             = aws_iam_role.lambda_role.arn
  handler          = each.value.handler
  runtime          = "python3.11"
  filename         = data.archive_file.lambda_zip[each.key].output_path
  source_code_hash = data.archive_file.lambda_zip[each.key].output_base64sha256
  timeout          = each.value.timeout
  description      = each.value.description

  environment {
    variables = {
      BUCKET_NAME      = var.bucket_name
      DDB_CHUNKS_TABLE = var.ddb_chunks_table
      DDB_THREADS      = var.ddb_threads_table
      DDB_EVENTS       = var.ddb_events_table
      DDB_TOKENS_TABLE = var.ddb_tokens_table
    }
  }
}

# CloudWatch Log Groups with retention
resource "aws_cloudwatch_log_group" "lambda_logs" {
  for_each = local.lambda_functions

  name              = "/aws/lambda/${aws_lambda_function.functions[each.key].function_name}"
  retention_in_days = 30

  tags = {
    Name = "${var.name}-${each.key}-logs"
  }
}