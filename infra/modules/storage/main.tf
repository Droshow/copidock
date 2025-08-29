resource "random_id" "suffix" { 
  byte_length = 4 
}

resource "aws_s3_bucket" "copidock" {
  bucket = "${var.name}-store-${random_id.suffix.hex}"
}

resource "aws_s3_bucket_public_access_block" "copidock" {
  bucket                  = aws_s3_bucket.copidock.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "copidock" {
  bucket = aws_s3_bucket.copidock.id
  rule { 
    apply_server_side_encryption_by_default { 
      sse_algorithm = "AES256" 
    } 
  }
}

resource "aws_s3_bucket_versioning" "copidock" {
  bucket = aws_s3_bucket.copidock.id
  versioning_configuration { 
    status = "Enabled" 
  }
}