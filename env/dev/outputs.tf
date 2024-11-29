output "aks_cluster_name" {
  value = module.aks.aks_name
}

output "kube_admin_config" {
  value = module.aks.kube_admin_config
  sensitive = true
}

output "kube_config" {
  value = module.aks.kube_config
  sensitive = true
}
