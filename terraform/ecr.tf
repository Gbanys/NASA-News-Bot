resource "aws_ecr_repository" "nasa_frontend_repository" {
  name                 = "nasa_frontend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  # Ensure the new repository is created before destroying the old one
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_ecr_repository" "nasa_backend_repository" {
  name                 = "nasa_backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  # Ensure the new repository is created before destroying the old one
  lifecycle {
    create_before_destroy = true
  }
}

resource "null_resource" "empty_ecr_frontend" {
  provisioner "local-exec" {
    command = <<EOT
    aws ecr list-images --repository-name ${aws_ecr_repository.nasa_frontend_repository.name} --query 'imageIds[*]' --output json | \
    jq -c '.[]' | \
    xargs -I {} aws ecr batch-delete-image --repository-name ${aws_ecr_repository.nasa_frontend_repository.name} --image-ids '{}'
    EOT
  }

  triggers = {
    always_run = "${timestamp()}"
  }
}

resource "null_resource" "empty_ecr_backend" {
  provisioner "local-exec" {
    command = <<EOT
    aws ecr list-images --repository-name ${aws_ecr_repository.nasa_backend_repository.name} --query 'imageIds[*]' --output json | \
    jq -c '.[]' | \
    xargs -I {} aws ecr batch-delete-image --repository-name ${aws_ecr_repository.nasa_backend_repository.name} --image-ids '{}'
    EOT
  }

  triggers = {
    always_run = "${timestamp()}"
  }
}
