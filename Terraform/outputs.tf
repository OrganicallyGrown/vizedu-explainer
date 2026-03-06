output "cloud_run_url" {
  description = "The URL of the deployed Cloud Run service"
  value       = google_cloud_run_service.vizedu.status[0].url
}

output "storage_bucket_name" {
  description = "Name of the created storage bucket"
  value       = google_storage_bucket.assets.name
}

output "service_name" {
  description = "Cloud Run service name"
  value       = google_cloud_run_service.vizedu.name
}