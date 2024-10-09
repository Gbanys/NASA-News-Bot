resource "aws_codepipeline" "codepipeline" {
  name     = "nasa-pipeline"
  role_arn = aws_iam_role.nasa_codepipeline_role.arn
  pipeline_type = "V2"

  artifact_store {
    location = aws_s3_bucket.nasa_codepipeline_bucket.bucket
    type     = "S3"

    encryption_key {
      id   = aws_kms_alias.nasa_s3_kms_alias.id
      type = "KMS"
    }
  }

  trigger {
    provider_type = "CodeStarSourceConnection"
    git_configuration {
      source_action_name = "Source"
      push{
        branches {
          includes = ["master"]
        }
      }
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