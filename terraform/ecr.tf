resource "aws_ecr_repository" "nasa_frontend_repository" {
  name                 = "nasa_frontend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "nasa_backend_repository" {
  name                 = "nasa_backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}