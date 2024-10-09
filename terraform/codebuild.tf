resource "aws_codebuild_project" "nasa_codebuild_project" {
  name          = "NasaCodeBuildProject"
  description   = "A CodeBuild project for NASA news bot application"
  build_timeout = 30 #

  source {
    type      = "GITHUB"
    location  = "https://github.com/Gbanys/NASA-News-Bot.git" # Change to your GitHub repo URL
    buildspec = "buildspec.yml" # Adjust if your buildspec is named differently
  }

  environment {
    compute_type = "BUILD_GENERAL1_SMALL"
    image        = "aws/codebuild/standard:5.0" # Adjust according to your needs
    type         = "LINUX_CONTAINER"

    environment_variable {
      name  = "ENV_VAR_NAME"
      value = "value"
    }
  }

  service_role = aws_iam_role.nasa_codebuild_role.arn

  artifacts {
    type = "S3"
    location = "${aws_s3_bucket.nasa_codepipeline_bucket.bucket}"
    packaging = "ZIP"
    name = "build-output.zip"
    override_artifact_name = true
  }
}

resource "aws_iam_role" "nasa_codebuild_role" {
  name = "nasa_codebuild_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Principal = {
        Service = "codebuild.amazonaws.com"
      }
      Effect = "Allow"
      Sid    = ""
    }]
  })
}

resource "aws_iam_role_policy_attachment" "nasa_codebuild_policy" {
  role       = aws_iam_role.nasa_codebuild_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSCodeBuildAdminAccess"
}

data "aws_iam_policy_document" "codebuild_logs_policy" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources=["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject"
    ]
    resources=["arn:aws:s3:::nasa-codepipeline-bucket/*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt"
    ]
    resources=[aws_kms_key.nasa_s3_kms_key.arn]
  }
}

resource "aws_iam_policy" "logs_policy" {
  name   = "nasa_codepipeline_codebuild_logs_policy"
  policy = data.aws_iam_policy_document.codebuild_logs_policy.json
}

resource "aws_iam_role_policy_attachment" "logs_policy_attachment" {
  role       = aws_iam_role.nasa_codebuild_role.name
  policy_arn = aws_iam_policy.logs_policy.arn
}