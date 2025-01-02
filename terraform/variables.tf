variable "eks_cluster_name" {
  description = "Nome do cluster EKS"
  type        = string
}

variable "namespace" {
  description = "Namespace para reiniciar o recurso"
  type        = string
  default     = "default"
}
