module "aks" {
  source = "../../modules/aks"

  cluster_name         = var.cluster_name
  location             = var.location
  resource_group_name  = var.resource_group_name
  dns_prefix           = var.dns_prefix
  kubernetes_version   = var.kubernetes_version
  default_node_count   = var.default_node_count
  user_node_count      = var.user_node_count
  tags                 = var.tags
}
