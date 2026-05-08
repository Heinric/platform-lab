variable "environment" {
  type = string
}

variable "cloud" {
  type = string
}

resource "kubernetes_namespace" "main" {
  metadata {
    name = "${var.cloud}-${var.environment}"

    labels = {
      cloud       = var.cloud
      environment = var.environment
      managed-by  = "terraform"
    }
  }
}

output "namespace" {
  value = kubernetes_namespace.main.metadata[0].name
}
