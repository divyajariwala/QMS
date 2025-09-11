locals {
  s3_origin_id = "${var.short_name}-s3FrontendOrigin"
}

resource "aws_cloudfront_origin_access_control" "origin_access_control" {
  name = "${var.short_name}-s3OriginAccessControl"
  origin_access_control_origin_type = "s3"
  signing_behavior = "always"
  signing_protocol = "sigv4"
}

resource "aws_cloudfront_distribution" "cloudfront_distribution" {
  origin {
    domain_name = aws_s3_bucket.static_website.bucket_domain_name
    origin_id = local.s3_origin_id
    origin_access_control_id = aws_cloudfront_origin_access_control.origin_access_control.id
  }
  default_root_object = "index.html"
  enabled = true
  default_cache_behavior {
    target_origin_id = local.s3_origin_id
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods = ["GET", "HEAD"]
    cache_policy_id = "658327ea-f89d-4fab-a63d-7e88639e58f6"
    response_headers_policy_id = "60669652-455b-4ae9-85a4-c4c02393f86c"
    min_ttl = 0
    default_ttl = 0
    max_ttl = 0
  }
  viewer_certificate {
    cloudfront_default_certificate = true
  }
  restrictions {
    geo_restriction {
      locations        = []
      restriction_type = "none"
    }
  }
}