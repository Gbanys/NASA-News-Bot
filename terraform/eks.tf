# module "vpc" {
#   source  = "terraform-aws-modules/vpc/aws"
#   version = "5.8.1"

#   name = "eks-vpc"

#   cidr = "10.0.0.0/16"

#   azs             = ["eu-west-2a", "eu-west-2b"]
#   private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
#   public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

#   enable_nat_gateway = true
#   enable_vpn_gateway = true
#   single_nat_gateway   = true
#   enable_dns_hostnames = true
# }

# module "eks" {
#   source  = "terraform-aws-modules/eks/aws"
#   version = "20.8.5"

#   cluster_name    = "nasa-dev-cluster"
#   cluster_version = "1.30"

#   cluster_endpoint_public_access           = true
#   enable_cluster_creator_admin_permissions = true

#   vpc_id     = module.vpc.vpc_id
#   subnet_ids = module.vpc.private_subnets

#   eks_managed_node_group_defaults = {
#     ami_type = "AL2_x86_64"
#   }

#   eks_managed_node_groups = {
#     one = {
#       name = "node-group-1"

#       instance_types = ["t3.small"]

#       min_size     = 1
#       max_size     = 3
#       desired_size = 2
#     }
#   }
# }