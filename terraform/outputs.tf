output "cluster_name" {
  description = "GKE Cluster name"
  value       = google_container_cluster.primary.name
}

output "cluster_endpoint" {
  description = "GKE Cluster endpoint"
  value       = google_container_cluster.primary.endpoint
  sensitive   = true
}

output "cluster_location" {
  description = "GKE Cluster location"
  value       = google_container_cluster.primary.location
}

output "ingress_ip" {
  description = "Static IP for ingress"
  value       = google_compute_global_address.ingress_ip.address
}

output "app_url" {
  description = "Application URL"
  value       = "https://${var.domain}"
}

output "kubectl_config" {
  description = "kubectl configuration command"
  value       = "gcloud container clusters get-credentials ${google_container_cluster.primary.name} --zone ${var.zone} --project ${var.project_id}"
}

