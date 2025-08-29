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
    actions   = ["s3:ListBucket"]
    resources = [var.bucket_arn]
  }

  statement {
    actions = [
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
      "dynamodb:Query",
      "dynamodb:BatchWriteItem"
    ]
    resources = var.table_arns
  }
}

resource "aws_iam_role_policy" "lambda_inline" {
  role   = aws_iam_role.lambda_role.id
  policy = data.aws_iam_policy_document.lambda_inline.json
}

# Create a placeholder ZIP file for Lambda
data "archive_file" "lambda_zip" {
  type        = "zip"
  output_path = "${path.module}/lambda_placeholder.zip"
  source {
    content  = "def handler(event, context): return {'statusCode': 200, 'body': 'Hello from Lambda!'}"
    filename = "lambda_function.py"
  }
}

resource "aws_lambda_function" "notes" {
  function_name    = "${var.name}-notes"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_function.handler"
  runtime         = "python3.11"
  filename        = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      BUCKET_NAME      = var.bucket_name
      DDB_CHUNKS_TABLE = var.ddb_chunks_table
      DDB_TOKENS_TABLE = var.ddb_tokens_table
      DDB_THREADS      = var.ddb_threads_table
      DDB_EVENTS       = var.ddb_events_table
    }
  }
}