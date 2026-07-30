# Migration Strategy: Moving Away from Facets to Open IaC

## Phase 1: Resource Inventory & State Discovery
- Export existing AWS configurations managed by Facets.
- Map state dependencies across database instances, network CIDRs, and secret references.

## Phase 2: Parallel Infrastructure Provisioning
- Author reusable Terraform modules for VPC, RDS, and ECR.
- Use `terraform import` for existing managed database and storage resources to avoid data migration risk.

## Phase 3: CI/CD Pipeline Shift
- Migrate deployment definitions from Facets platform workflows into declarative GitHub Actions pipelines using Helm and OpenTofu/Terraform.

## Phase 4: Zero-Downtime Traffic Migration
1. Provision target Kubernetes namespaces via Helm/Kustomize.
2. Spin up worker processes pointing to the target queue.
3. Shift external ingress traffic via weighted DNS routing (10% -> 50% -> 100%).
4. Decommission Facets management wrappers once monitoring confirms zero traffic on legacy paths.