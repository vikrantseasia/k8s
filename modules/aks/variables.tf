variable "cluster_name" {
  description = "Name of the AKS cluster"
  type        = string
}

variable "location" {
  description = "Location of the AKS cluster"
  type        = string
}

variable "resource_group_name" {
  description = "Resource group name for the AKS cluster"
  type        = string
}

variable "dns_prefix" {
  description = "DNS prefix for the AKS cluster"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version for the AKS cluster"
  type        = string
}

variable "default_node_count" {
  description = "Node count for the default system node pool"
  type        = number
}

variable "user_node_count" {
  description = "Node count for the user node pool"
  type        = number
}

variable "tags" {
  description = "Tags to be applied to the AKS resources"
  type        = map(string)
}
