resource "aws_sns_topic" "admin-sns-topic" {
  name = "admin-sns-topic"
}

resource "aws_sns_topic_subscription" "admin_email_subscription" {
  topic_arn = aws_sns_topic.admin-sns-topic.arn
  protocol  = "email"
  endpoint  = "giedriusbanys150@proton.me"
}

resource "aws_sns_topic_policy" "admin-sns-topic-policy" {
  arn = aws_sns_topic.admin-sns-topic.arn

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "codestar-notifications.amazonaws.com"
        },
        Action   = "SNS:Publish",
        Resource = aws_sns_topic.admin-sns-topic.arn
      }
    ]
  })
}
