terraform {
  required_providers {
    kind = {
      source = "tehcyx/kind"
      version = "0.2.0"
    }
  }
  
}

provider "kind" {}


resource "kind_cluster" "default" {
    name = "gdm-local"
    kubeconfig_path = pathexpand("~/.kube/config")
}