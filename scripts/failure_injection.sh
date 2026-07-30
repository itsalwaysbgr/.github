#!/usr/bin/env bash
set -euo pipefail

echo "========================================================="
echo " PulseOps Controlled Failure & Rollback Demonstration"
echo "========================================================="

echo "[1/5] Starting fresh healthy local environment..."
docker compose up -d --build
sleep 10

echo "[2/5] Verifying initial health status via smoke test..."
python3 scripts/smoke_test.py --base-url http://localhost:8000

echo "[3/5] Injecting controlled failure: Setting invalid DB_HOST in API service..."
docker compose exec -T api export DB_HOST="invalid_db_host_xyz" || true
docker compose stop api
docker compose run -d -e DB_HOST="invalid_db_host_xyz" --name broken_api -p 8000:8000 api

echo "[4/5] Executing smoke test against broken API (Expecting Failure)..."
if python3 scripts/smoke_test.py --base-url http://localhost:8000; then
    echo "ERROR: Smoke test passed when it should have failed!"
    exit 1
else
    echo "CONFIRMED: Smoke test caught the failure as expected!"
fi

echo "[5/5] Executing Rollback: Restoring original healthy API instance..."
docker rm -f broken_api
docker compose start api
sleep 5

echo "Verifying restored state with smoke test..."
python3 scripts/smoke_test.py --base-url http://localhost:8000

echo "========================================================="
echo " FAILURE INJECTION & ROLLBACK DEMONSTRATION COMPLETE"
echo "========================================================="