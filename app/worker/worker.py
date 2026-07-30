import os
import json
import time
import signal
import sys
import psycopg2
import redis

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "pulseops")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "postgres")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

running = True

def signal_handler(sig, frame):
    global running
    print("[WORKER] Graceful shutdown signal received. Finishing in-flight task...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def get_db():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        connect_timeout=3
    )

def update_job_status(job_id, status, result=None):
    try:
        conn = get_db()
        cur = conn.cursor()
        if result:
            cur.execute(
                "UPDATE jobs SET status = %s, result = %s, updated_at = CURRENT_TIMESTAMP WHERE job_id = %s",
                (status, result, job_id)
            )
        else:
            cur.execute(
                "UPDATE jobs SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE job_id = %s",
                (status, job_id)
            )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[WORKER] Failed to update job status for {job_id}: {e}")

def main():
    print("[WORKER] Background processing worker initializing...")
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

    while running:
        try:
            item = r.blpop("job_queue", timeout=2)
            if item:
                _, payload = item
                data = json.loads(payload.decode('utf-8'))
                job_id = data["job_id"]
                input_data = data["input_data"]

                print(f"[WORKER] Processing job {job_id}")
                update_job_status(job_id, "PROCESSING")

                # Core business logic transformation
                time.sleep(1) # Simulate asynchronous work
                result = input_data.upper()

                update_job_status(job_id, "COMPLETED", result)
                print(f"[WORKER] Successfully completed job {job_id} -> Result: {result}")
        except Exception as e:
            if running:
                print(f"[WORKER] Error in processing loop: {e}")
            time.sleep(1)

    print("[WORKER] Worker shutdown clean and complete.")

if __name__ == "__main__":
    main()