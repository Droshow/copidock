locals {
  dynamodb_tables = {
    chunks = {
      hash_key   = "ns"
      range_key  = "sort"
      attributes = {
        ns   = "S"
        sort = "S"
      }
    }
    tokens = {
      hash_key   = "tok"
      range_key  = "ns_ts_id"
      attributes = {
        tok      = "S"
        ns_ts_id = "S"
      }
    }
    threads = {
      hash_key   = "thread_id"
      range_key  = null
      attributes = {
        thread_id = "S"
      }
    }
    events = {
      hash_key   = "thread_id"
      range_key  = "at"
      attributes = {
        thread_id = "S"
        at        = "S"
      }
    }
  }
}

resource "aws_dynamodb_table" "tables" {
  for_each = local.dynamodb_tables

  name         = "${var.name}-${each.key}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = each.value.hash_key
  range_key    = each.value.range_key

  dynamic "attribute" {
    for_each = each.value.attributes
    content {
      name = attribute.key
      type = attribute.value
    }
  }

  tags = {
    Name        = "${var.name}-${each.key}"
    Environment = var.environment
    Project     = var.name
  }

  point_in_time_recovery {
    enabled = var.enable_point_in_time_recovery
  }

  lifecycle {
    prevent_destroy = true
  }
}