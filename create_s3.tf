module "all_s3_buckets" {
  source      = "./aws/modules/s3"
  count       = length(var.s3_buckets_list)
  bucket_name = "${var.short_name}-${var.environment}-${var.s3_buckets_list[count.index]}"
  tags = {
    "Name"      = "${var.s3_buckets_list[count.index]}-bucket"
    "component" = "s3"
  }
}