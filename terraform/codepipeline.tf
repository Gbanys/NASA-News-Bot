resource "aws_codepipeline" "codepipeline" {
  name     = "nasa-pipeline"
  role_arn = aws_iam_role.nasa_codepipeline_role.arn

  artifact_store {
    location = aws_s3_bucket.nasa_codepipeline_bucket.bucket
    type     = "S3"

    encryption_key {
      id   = aws_kms_alias.nasa_s3_kms_alias.id
      type = "KMS"
    }
  }

  stage {
    name = "Source"

    action {
      name             = "Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["source_output"]

      configuration = {
        ConnectionArn    = aws_codestarconnections_connection.nasa_repository_connection.arn
        FullRepositoryId = "Gbanys/NASA-News-Bot"
        BranchName       = "master"
      }
    }
  }

  stage {
    name = "Build"

    action {
      name             = "Build"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["build_output"]
      version          = "1"

      configuration = {
        ProjectName = aws_codebuild_project.nasa_codebuild_project.name
      }
    }
  }

  stage {
    name = "Deploy"

    action {
      name            = "Deploy"
      category        = "Deploy"
      owner           = "AWS"
      provider        = "CloudFormation"
      input_artifacts = ["build_output"]
      version         = "1"

      configuration = {
        ActionMode     = "REPLACE_ON_FAILURE"
        Capabilities   = "CAPABILITY_AUTO_EXPAND,CAPABILITY_IAM"
        OutputFileName = "CreateStackOutput.json"
        StackName      = "MyStack"
        TemplatePath   = "build_output::sam-templated.yaml"
      }
    }
  }
}

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

resource "aws_codestarconnections_connection" "nasa_repository_connection" {
  name          = "nasa-repository-connection"
  provider_type = "GitHub"
}

resource "aws_s3_bucket" "nasa_codepipeline_bucket" {
  bucket = "nasa-codepipeline-bucket"
}

resource "aws_s3_bucket_public_access_block" "nasa_codepipeline_bucket_pab" {
  bucket = aws_s3_bucket.nasa_codepipeline_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["codepipeline.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "nasa_codepipeline_role" {
  name               = "nasa-codepipeline-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

data "aws_iam_policy_document" "kms_policy" {
  statement {
    effect = "Allow"

    actions = [
      "kms:Decrypt",
      "kms:Encrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:DescribeKey"
    ]

    resources = [aws_kms_key.nasa_s3_kms_key.arn]
  }
}

resource "aws_iam_policy" "kms_policy" {
  name   = "nasa_codepipeline_kms_policy"
  policy = data.aws_iam_policy_document.kms_policy.json
}

resource "aws_iam_role_policy_attachment" "kms_policy_attachment" {
  role       = aws_iam_role.nasa_codepipeline_role.name
  policy_arn = aws_iam_policy.kms_policy.arn
}

data "aws_iam_policy_document" "nasa_codepipeline_policy" {
  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:GetBucketVersioning",
      "s3:PutObjectAcl",
      "s3:PutObject",
    ]

    resources = [
      aws_s3_bucket.nasa_codepipeline_bucket.arn,
      "${aws_s3_bucket.nasa_codepipeline_bucket.arn}/*"
    ]
  }

  statement {
    effect    = "Allow"
    actions   = ["codestar-connections:UseConnection"]
    resources = [aws_codestarconnections_connection.nasa_repository_connection.arn]
  }

  statement {
    effect = "Allow"

    actions = [
      "codebuild:BatchGetBuilds",
      "codebuild:StartBuild",
    ]

    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "nasa_codepipeline_policy" {
  name   = "nasa_codepipeline_policy"
  role   = aws_iam_role.nasa_codepipeline_role.id
  policy = data.aws_iam_policy_document.nasa_codepipeline_policy.json
}

resource "aws_kms_key" "nasa_s3_kms_key" {
  description             = "KMS key for encrypting S3 bucket"
  key_usage               = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

resource "aws_kms_alias" "nasa_s3_kms_alias" {
  name          = "alias/NasaS3KmsKey"
  target_key_id = aws_kms_key.nasa_s3_kms_key.id
}