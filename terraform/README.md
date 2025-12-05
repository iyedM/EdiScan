# Terraform - GCP Infrastructure

## Prerequisites

- Google Cloud SDK installed
- Terraform >= 1.0
- GCP Project with billing enabled

## Setup

```bash
# Authenticate with GCP
gcloud auth application-default login

# Create state bucket
gsutil mb gs://ediscan-terraform-state

# Copy and edit variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

## Deploy

```bash
# Initialize
terraform init

# Plan
terraform plan

# Apply
terraform apply
```

## Connect to Cluster

```bash
# Get credentials (shown in terraform output)
gcloud container clusters get-credentials ediscan-cluster \
  --zone europe-west1-b \
  --project YOUR_PROJECT_ID
```

## Destroy

```bash
terraform destroy
```

## Outputs

| Output | Description |
|--------|-------------|
| `cluster_endpoint` | GKE cluster endpoint |
| `ingress_ip` | Static IP for ingress |
| `app_url` | Application URL |

