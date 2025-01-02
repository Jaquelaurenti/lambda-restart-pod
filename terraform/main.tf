module "lambda" {
  source          = "./modules/lambda"
  eks_cluster_name = var.eks_cluster_name
  namespace       = var.namespace
}