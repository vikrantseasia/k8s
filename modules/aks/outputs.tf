output "aks_name" {
  value = azurerm_kubernetes_cluster.aks.name
}

output "kube_admin_config" {
  value = azurerm_kubernetes_cluster.aks.kube_admin_config_raw
  sensitive = true
}

output "kube_config" {
  value = azurerm_kubernetes_cluster.aks.kube_config_raw
  sensitive = true
}
