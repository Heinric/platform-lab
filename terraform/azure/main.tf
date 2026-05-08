terraform {
  required_version = ">= 1.0"

  backend "local" {
    path = "../../.tfstate/azure/terraform.tfstate"
  }

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = "kind-azure"
}

module "namespace" {
  source      = "../modules/kubernetes"
  cloud       = "azure"
  environment = "dev"
}

output "namespace" {
  value = module.namespace.namespace
}
