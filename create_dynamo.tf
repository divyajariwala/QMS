resource "aws_dynamodb_table" "dynamodb_tables" {
  count = length(var.dynamodb_configs)
  name = "${var.short_name}-${var.environment}-${var.dynamodb_configs[count.index].table_name}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = var.dynamodb_configs[count.index].part_key.key_name

  attribute {
    name = var.dynamodb_configs[count.index].part_key.key_name
    type = var.dynamodb_configs[count.index].part_key.key_type
  }

  dynamic "attribute" {
    for_each = var.dynamodb_configs[count.index].sort_key[*]
    content {
      name = attribute.value.key_name
      type = attribute.value.key_type
    }
  }

  range_key = try(var.dynamodb_configs[count.index].sort_key.key_name, null)
}