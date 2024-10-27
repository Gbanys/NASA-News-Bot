
resource "aws_cognito_user_pool" "nasa_app_user_pool" {
  name              = "nasa-app-user-pool"
  mfa_configuration = "OFF"

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_uppercase = true
    require_numbers   = true
    require_symbols   = false
  }

  auto_verified_attributes = ["email"]

  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
    email_message        = "Your verification code is {####}"
    email_subject        = "Verify your account"
  }

  schema {
    attribute_data_type = "String"
    name                = "email"
    required            = true
    mutable             = true
    string_attribute_constraints {
      min_length = 5
      max_length = 50
    }
  }

  tags = {
    Environment = "dev"
  }
}

resource "aws_iam_role" "cognito_sns_role" {
  name = "Cognito-SNS-Role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "cognito-idp.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "cognito_sns_policy" {
  name        = "Cognito-SNS-Policy"
  description = "Policy to allow Cognito to send SMS messages"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "attach_cognito_sns_policy" {
  role       = aws_iam_role.cognito_sns_role.name
  policy_arn = aws_iam_policy.cognito_sns_policy.arn
}

resource "aws_cognito_user_pool_client" "nasa_chatbot_app_client" {
  name         = "nasa-chatbot-client"
  user_pool_id = aws_cognito_user_pool.nasa_app_user_pool.id

  allowed_oauth_flows                  = ["code", "implicit"]
  allowed_oauth_scopes                 = ["email", "openid", "profile"]
  allowed_oauth_flows_user_pool_client = true
  supported_identity_providers         = ["COGNITO"]

  callback_urls = ["http://localhost:8000/callback"]

  generate_secret = true
}

resource "aws_cognito_user_pool_domain" "nasa_chatbot_domain" {
  domain       = "nasachatbot"
  user_pool_id = aws_cognito_user_pool.nasa_app_user_pool.id
}