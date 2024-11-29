resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.cluster_name
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = var.dns_prefix

  kubernetes_version = var.kubernetes_version
  sku_tier           = "Standard" # Set pricing tier to Standard (required for Dev/Test)

  default_node_pool {
    name       = "systempool"
    vm_size    = "Standard_D4ds_v5"
    node_count = var.default_node_count
    type       = "VirtualMachineScaleSets"
    enable_auto_scaling = true
    min_count = 1
    max_count = 2
  }

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

resource "azurerm_kubernetes_cluster_node_pool" "userpool" {
  name                = "userpool"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks.id
  vm_size             = "Standard_D4ds_v5"
  node_count          = var.user_node_count
  mode                = "User"
  orchestrator_version = var.kubernetes_version
  enable_auto_scaling = false # Optional: Can be enabled if needed
  tags                = var.tags
}
