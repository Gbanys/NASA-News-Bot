resource "aws_ecr_repository" "nasa_frontend_repository" {
  name                 = "nasa_frontend_project_repository"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}