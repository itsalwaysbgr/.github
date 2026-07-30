#!/usr/bin/env python3
import argparse
import time
import sys
import requests

def run_smoke_test(base_url, timeout=30):
    print(f"[1/4] Checking readiness endpoint at {base_url}/health/ready...")
    try:
        r = requests.get(f"{base_url}/health/ready", timeout=5)
        if r.status_code != 200:
            print(f"FAILED: Readiness endpoint returned HTTP {r.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"FAILED: Could not reach readiness endpoint: {e}")
        sys.exit(1)

    payload_text = "smoke test validation payload"
    print(f"[2/4] Submitting test job: '{payload_text}'...")
    try:
        r = requests.post(f"{base_url}/jobs", json={"input_data": payload_text}, timeout=5)
        if r.status_code != 202:
            print(f"FAILED: Job creation failed with HTTP {r.status_code}")
            sys.exit(1)
        job_id = r.json()["job_id"]
        print(f"Job queued successfully. ID: {job_id}")
    except Exception as e:
        print(f"FAILED: Job submission request error: {e}")
        sys.exit(1)

    print(f"[3/4] Polling job {job_id} until completion (Timeout: {timeout}s)...")
    start_time = time.time()
    completed = False

    while time.time() - start_time < timeout:
        try:
            r = requests.get(f"{base_url}/jobs/{job_id}", timeout=5)
            if r.status_code == 200:
                data = r.json()
                status = data.get("status")
                print(f"Current status: {status}")
                if status == "COMPLETED":
                    result = data.get("result")
                    expected_result = payload_text.upper()
                    print(f"[4/4] Job COMPLETED! Received result: '{result}'")
                    if result == expected_result:
                        print("SUCCESS: End-to-end business logic verified.")
                        completed = True
                        break
                    else:
                        print(f"FAILED: Transformation mismatch. Expected '{expected_result}', got '{result}'")
                        sys.exit(1)
        except Exception as e:
            print(f"Warning: Exception while polling: {e}")
        time.sleep(2)

    if not completed:
        print("FAILED: Job did not reach COMPLETED state within time limit.")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PulseOps Smoke Test")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    args = parser.parse_args()
    run_smoke_test(args.base_url)