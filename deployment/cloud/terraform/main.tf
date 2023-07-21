terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "4.51.0"
    }
  }
}

variable "project_id" {
  default     = "group8-391123"
  description = "project id"
}

variable "region" {
  default     = "us-central1"
  description = "region"
}

variable "zone" {
  default     = "us-central1-c"
  description = "zone"
}

output "region" {
  value       = var.region
  description = "GCloud Region"
}

output "project_id" {
  value       = var.project_id
  description = "GCloud Project ID"
}

output "kubernetes_cluster_name" {
  value       = google_container_cluster.primary.name
  description = "GKE Cluster Name"
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

resource "google_artifact_registry_repository" "my-repo" {
  location      = var.region
  repository_id = "gdm"
  description   = "docker repository for GDM"
  format        = "DOCKER"
}

resource "google_container_cluster" "primary" {
  name     = "gdm-cloud"
  location = var.region
  enable_autopilot = true
  ip_allocation_policy {
  }
  release_channel {
    channel = "REGULAR"
  }
}
