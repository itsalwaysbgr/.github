# Deployment Runbook

## Purpose
This runbook covers how to build, deploy, and verify the PulseOps application in a local Docker or Kubernetes environment.

## Prerequisites
- Docker and Docker Compose installed
- Python 3.11+ for local smoke testing
- Access to the repository root

## Local Deployment
### 1. Build and start services
```bash
docker compose up --build -d
```

### 2. Verify service health
```bash
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```

### 3. Submit a test job
```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"input_data":"deployment smoke test"}'
```

### 4. Run smoke tests
```bash
python scripts/smoke_test.py --base-url http://localhost:8000
```

## Kubernetes Deployment
### 1. Apply manifests
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/api-service.yaml
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/worker-deployment.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/network-policy.yaml
```

### 2. Verify rollout
```bash
kubectl get pods -n pulseops
kubectl get svc -n pulseops
kubectl get ingress -n pulseops
```

## Rollback
If a deployment introduces regressions:
1. Revert the latest deployment manifest or image tag change.
2. Redeploy the previous stable version.
3. Re-run the smoke test and health checks.

## Common Issues
- API fails readiness: confirm PostgreSQL and Redis are reachable.
- Frontend cannot reach API: verify the nginx proxy route and service DNS.
- Job stays queued: check the worker pod and Redis queue health.
