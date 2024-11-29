variable "location" {
  default = "East US 2"
}

variable "resource_group_name" {
  default = "aks-terraform"
}

variable "cluster_name" {
  default = "aksdemo"
}

variable "dns_prefix" {
  default = "aksdemodns"
}

variable "kubernetes_version" {
  default = "1.28.11"
}

variable "default_node_count" {
  default = 1
}

variable "user_node_count" {
  default = 2
}


variable "tags" {
  default = {
    environment = "dev"
    purpose     = "Dev/Test"
    owner       = "my-team"
  }
}
