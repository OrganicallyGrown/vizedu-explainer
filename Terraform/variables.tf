variable "project_id" {
  description = "The Google Cloud project ID"
  type        = string
}

variable "region" {
  description = "The Google Cloud region for resources"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Name of the Cloud Run service"
  type        = string
  default     = "vizedu-explainer"
}

variable "bucket_name" {
  description = "Name of the Cloud Storage bucket for assets"
  type        = string
}

variable "image" {
  description = "Container image to deploy (after building)"
  type        = string
  default     = ""  # Will be set after gcloud builds or manual build
}