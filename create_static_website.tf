resource "aws_s3_bucket" "static_website" {
  bucket = "${var.short_name}-${var.environment}-${var.static_website}"
  force_destroy = true
  tags = {
    "Name" = "${var.static_website}-bucket"
    "component" = "s3"
  }
}

resource "aws_s3_bucket_ownership_controls" "static_website_controls" {
  bucket = aws_s3_bucket.static_website.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_public_access_block" "static_website_block" {
  bucket = aws_s3_bucket.static_website.id
  block_public_acls = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_acl" "static_website_acl" {
  depends_on = [
    aws_s3_bucket_ownership_controls.static_website_controls,
    aws_s3_bucket_public_access_block.static_website_block,
  ]
  bucket = aws_s3_bucket.static_website.id
  acl = "private"
}

resource "aws_s3_bucket_website_configuration" "bucket_website_configuration" {
  bucket = aws_s3_bucket.static_website.id
  index_document {
    suffix = "index.html"
  }
}

resource "aws_s3_bucket_policy" "bucket_website_policy" {
  bucket = aws_s3_bucket.static_website.id
  policy = jsonencode({
    "Statement" : [{
      "Action" : ["s3:GetObject"],
      "Effect" : "Allow",
      "Resource" : "${aws_s3_bucket.static_website.arn}/*",
      "Principal" : {
        "Service" : "cloudfront.amazonaws.com"
      }
      "Condition" : {
        "StringEquals" : {
          "AWS:SourceArn" : "${aws_cloudfront_distribution.cloudfront_distribution.arn}"
        }
      }
    }]
    "Version" : "2008-10-17"
  })
}