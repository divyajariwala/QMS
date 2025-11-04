resource "aws_dynamodb_table" "dynamodb_tables" {
  count        = length(var.dynamodb_configs)
  name         = "${var.short_name}-${var.environment}-${var.dynamodb_configs[count.index].table_name}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = var.dynamodb_configs[count.index].part_key.key_name
  range_key    = try(var.dynamodb_configs[count.index].sort_key.key_name, null)

  # Consolidated attributes (PK, optional SK, plus all GSI key attributes), de-duped by name
  dynamic "attribute" {
    for_each = {
      for a in concat(
        [
          {
            name = var.dynamodb_configs[count.index].part_key.key_name
            type = var.dynamodb_configs[count.index].part_key.key_type
          }
        ],
        try(var.dynamodb_configs[count.index].sort_key.key_name, null) != null ?
        [
          {
            name = var.dynamodb_configs[count.index].sort_key.key_name
            type = var.dynamodb_configs[count.index].sort_key.key_type
          }
        ] : [],
        flatten([
          for gsi in try(var.dynamodb_configs[count.index].global_secondary_indexes, []) : concat(
            [
              {
                name = gsi.hash_key
                type = try(gsi.hash_key_type, "S")
              }
            ],
            try(gsi.range_key, null) != null ? [
              {
                name = gsi.range_key
                type = try(gsi.range_key_type, "S")
              }
            ] : []
          )
        ])
      ) : a.name => a
    }

    content {
      name = attribute.value.name
      type = attribute.value.type
    }
  }

  # Global Secondary Indexes (works with PAY_PER_REQUEST: no capacities set)
  dynamic "global_secondary_index" {
    for_each = try(var.dynamodb_configs[count.index].global_secondary_indexes, [])
    content {
      name               = global_secondary_index.value.name
      hash_key           = global_secondary_index.value.hash_key
      range_key          = try(global_secondary_index.value.range_key, null)
      projection_type    = global_secondary_index.value.projection_type
      non_key_attributes = try(global_secondary_index.value.non_key_attributes, null)
      # No read_capacity/write_capacity since we're using PAY_PER_REQUEST
    }
  }
}
