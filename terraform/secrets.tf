resource "random_password" "nasa_chatbot_session_middleware_secret_key" {
  length  = 32
  special = false
}

# Store Cognito User Pool ID
resource "aws_ssm_parameter" "cognito_user_pool_id" {
  name  = "/nasa_chatbot/cognito_user_pool_id"
  type  = "SecureString"
  value = aws_cognito_user_pool.nasa_app_user_pool.id
}

# Store Cognito App Client ID
resource "aws_ssm_parameter" "cognito_app_client_id" {
  name  = "/nasa_chatbot/cognito_app_client_id"
  type  = "SecureString"
  value = aws_cognito_user_pool_client.nasa_chatbot_app_client.id
}

# Store Cognito App Client Secret
resource "aws_ssm_parameter" "cognito_app_client_secret" {
  name  = "/nasa_chatbot/cognito_app_client_secret"
  type  = "SecureString"
  value = aws_cognito_user_pool_client.nasa_chatbot_app_client.client_secret
}

# Store Cognito Domain
resource "aws_ssm_parameter" "cognito_domain" {
  name  = "/nasa_chatbot/cognito_domain"
  type  = "SecureString"
  value = "${aws_cognito_user_pool_domain.nasa_chatbot_domain.domain}.auth.eu-west-2.amazoncognito.com"
}

# Store Secret Key
resource "aws_ssm_parameter" "secret_key" {
  name  = "/nasa_chatbot/secret_key"
  type  = "SecureString"
  value = random_password.nasa_chatbot_session_middleware_secret_key.result
}

resource "aws_ssm_parameter" "token_signing_key_url" {
  name  = "/nasa_chatbot/token_signing_key_url"
  type  = "SecureString"
  value = "https://cognito-idp.${var.aws_region}.amazonaws.com/${aws_cognito_user_pool.nasa_app_user_pool.id}/.well-known/jwks.json"
}