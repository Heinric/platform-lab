terraform {
  required_version = ">= 1.0"

  backend "local" {
    path = "../../.tfstate/aws/terraform.tfstate"
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
  config_context = "kind-aws"
}

module "namespace" {
  source      = "../modules/kubernetes"
  cloud       = "aws"
  environment = "dev"
}

output "namespace" {
  value = module.namespace.namespace
}
