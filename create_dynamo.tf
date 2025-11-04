resource "aws_dynamodb_table" "dynamodb_tables" {
  count        = length(var.dynamodb_configs)
  name         = "${var.short_name}-${var.environment}-${var.dynamodb_configs[count.index].table_name}"
  billing_mode = "PAY_PER_REQUEST"

  # PK / SK
  hash_key  = var.dynamodb_configs[count.index].part_key.key_name
  range_key = try(var.dynamodb_configs[count.index].sort_key.key_name, null)

  # Attribute: PK
  attribute {
    name = var.dynamodb_configs[count.index].part_key.key_name
    type = var.dynamodb_configs[count.index].part_key.key_type
  }

  # Attribute: optional SK
  dynamic "attribute" {
    for_each = try(var.dynamodb_configs[count.index].sort_key.key_name, null) != null ? [1] : []
    content {
      name = var.dynamodb_configs[count.index].sort_key.key_name
      type = var.dynamodb_configs[count.index].sort_key.key_type
    }
  }

  # Attribute: all GSI key attributes (deduped, exclude PK/SK)
  dynamic "attribute" {
    for_each = {
      for k in toset(flatten([
        for g in try(var.dynamodb_configs[count.index].global_secondary_indexes, []) :
        concat(
          [ g.hash_key ],
          try(g.range_key, null) != null ? [ g.range_key ] : []
        )
      ])) :
      k => k
      if k != var.dynamodb_configs[count.index].part_key.key_name &&
         k != try(var.dynamodb_configs[count.index].sort_key.key_name, "")
    }
    content {
      name = attribute.key
      # Default to "S" unless you add *_key_type fields in your vars
      type = "S"
    }
  }

  # GSIs WITHOUT a range key
  dynamic "global_secondary_index" {
    for_each = [
      for g in try(var.dynamodb_configs[count.index].global_secondary_indexes, []) :
      g if try(g.range_key, null) == null
    ]
    content {
      name               = global_secondary_index.value.name
      hash_key           = global_secondary_index.value.hash_key
      projection_type    = global_secondary_index.value.projection_type
      non_key_attributes = try(global_secondary_index.value.non_key_attributes, null)
    }
  }

  # GSIs WITH a range key
  dynamic "global_secondary_index" {
    for_each = [
      for g in try(var.dynamodb_configs[count.index].global_secondary_indexes, []) :
      g if try(g.range_key, null) != null
    ]
    content {
      name               = global_secondary_index.value.name
      hash_key           = global_secondary_index.value.hash_key
      range_key          = global_secondary_index.value.range_key
      projection_type    = global_secondary_index.value.projection_type
      non_key_attributes = try(global_secondary_index.value.non_key_attributes, null)
    }
  }
}
