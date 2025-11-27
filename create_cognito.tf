resource "aws_cognito_user_pool" "cognito_user_pool" {
  name = "${var.short_name}-${var.environment}-user-pool"
}

resource "aws_cognito_user_pool_domain" "user_pool_domain" {
  domain       = "${var.short_name}-${var.environment}"
  user_pool_id = aws_cognito_user_pool.cognito_user_pool.id
}

resource "aws_cognito_user_pool_client" "spa_client" {
  name         = "${var.short_name}-${var.environment}-client"
  user_pool_id = aws_cognito_user_pool.cognito_user_pool.id
  generate_secret = false
  callback_urls = [
    "https://${aws_cloudfront_distribution.cloudfront_distribution.domain_name}/auth/callback",
  ]
  allowed_oauth_flows = ["code"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes = [
    "openid",
    "email",
    "profile",
    "uid"
  ]
  supported_identity_providers = [
    "COGNITO",
    "OpenAM",
  ]
  explicit_auth_flows = [
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_USER_PASSWORD_AUTH",
  ]
  prevent_user_existence_errors = "ENABLED"
}

resource "aws_cognito_identity_provider" "cognito_identity_provider" {
  user_pool_id  = aws_cognito_user_pool.cognito_user_pool.id
  provider_name = "OpenAM"
  provider_type = "OIDC"
  provider_details = {
    client_id                 = var.openam_client_id
    client_secret             = var.openam_client_secret
    oidc_issuer               = var.openam_issuer
    attributes_request_method = "GET"
    authorize_scopes          = "openid email profile uid"
    authorize_url             = "${var.openam_issuer}/authorize"
    token_url                 = "${var.openam_issuer}/access_token"
    attributes_url            = "${var.openam_issuer}/userinfo"
    jwks_uri                  = "${var.openam_issuer}/.well-known/jwks.json"
  }
  attribute_mapping = {
    "email"        = "email"
    "given_name"   = "given_name"
    "family_name"  = "family_name"
    "preferred_username" = "uid"
  }
}
