output "vpc_id" {
  value       = module.vpc.vpc_id
  description = "Provisioned VPC ID"
}

output "api_ecr_repository_url" {
  value       = aws_ecr_repository.api.repository_url
  description = "ECR Repository URL for API Service"
}

output "worker_ecr_repository_url" {
  value       = aws_ecr_repository.worker.repository_url
  description = "ECR Repository URL for Background Worker"
}