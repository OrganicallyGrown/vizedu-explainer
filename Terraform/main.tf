# ------------------------------------------------------------------------------
# 1. Cloud Storage Bucket for generated images & audio
# ------------------------------------------------------------------------------

resource "google_storage_bucket" "assets" {
  name                        = var.bucket_name
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true   # for easier cleanup during dev

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30  # optional: auto-delete files older than 30 days
    }
  }
}

# Make bucket publicly readable (needed for signed/public URLs in the app)
resource "google_storage_bucket_iam_member" "public_read" {
  bucket = google_storage_bucket.assets.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

# ------------------------------------------------------------------------------
# 2. Cloud Run Service
# ------------------------------------------------------------------------------

resource "google_cloud_run_service" "vizedu" {
  name     = var.service_name
  location = var.region

  autogenerate_revision_name = true

  template {
    spec {
      containers {
        image = var.image != "" ? var.image : "gcr.io/cloudrun/hello"  # placeholder - replace after build

        ports {
          container_port = 8080
        }

        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }

        env {
          name  = "GCS_BUCKET_NAME"
          value = google_storage_bucket.assets.name
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "2Gi"
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Allow unauthenticated invocations (public access)
resource "google_cloud_run_service_iam_member" "public_invoker" {
  service  = google_cloud_run_service.vizedu.name
  location = google_cloud_run_service.vizedu.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}