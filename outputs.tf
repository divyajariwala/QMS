output "cloudfront_endpoint" {
  value = "https://${aws_cloudfront_distribution.cloudfront_distribution.domain_name}"
}

# output "api_gateway_endpoint" {
#   value = aws_api_gateway_stage.api_stage.invoke_url
# }

output "alb_dns_name" {
  value = "http://${aws_lb.ecs_alb_internal.dns_name}"
}

output "static_website_bucket_name" {
  value = aws_s3_bucket.static_website.bucket
}