resource "aws_secretsmanager_secret" "nasa_chatbot_secrets" {
  name        = "nasa_chatbot_cognito_secrets"
  description = "Secrets for NASA Chatbot Cognito Configuration"
}

resource "random_password" "nasa_chatbot_session_middleware_secret_key" {
  length  = 32
  special = false
}

resource "aws_secretsmanager_secret_version" "nasa_chatbot_secret_versions" {
  secret_id = aws_secretsmanager_secret.nasa_chatbot_secrets.id
  secret_string = jsonencode({
    cognito_user_pool_id      = aws_cognito_user_pool.nasa_app_user_pool.id
    cognito_app_client_id     = aws_cognito_user_pool_client.nasa_chatbot_app_client.id
    cognito_app_client_secret = aws_cognito_user_pool_client.nasa_chatbot_app_client.client_secret
    cognito_domain            = "${aws_cognito_user_pool_domain.nasa_chatbot_domain.domain}.auth.eu-west-2.amazoncognito.com"
    secret_key                = random_password.nasa_chatbot_session_middleware_secret_key.result
  })
}