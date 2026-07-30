import os
import json
import uuid
import time
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="PulseOps API Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "pulseops")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "postgres")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

def get_db():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        connect_timeout=3,
        cursor_factory=RealDictCursor
    )

def get_redis():
    return redis.Redis(host=REDIS_HOST, port=6379, db=0, socket_timeout=3)

class JobRequest(BaseModel):
    input_data: str

@app.on_event("startup")
def setup_db():
    for attempt in range(10):
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id VARCHAR(36) PRIMARY KEY,
                    input_data TEXT NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    result TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
            break
        except Exception as e:
            print(f"Database initialization attempt {attempt + 1} failed: {e}")
            time.sleep(2)

@app.get("/health/live")
def liveness():
    return {"status": "alive"}

@app.get("/health/ready")
def readiness():
    try:
        conn = get_db()
        conn.close()
        r = get_redis()
        r.ping()
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Unhealthy dependency: {str(e)}")

@app.post("/jobs", status_code=status.HTTP_202_ACCEPTED)
def create_job(job: JobRequest):
    job_id = str(uuid.uuid4())
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO jobs (job_id, input_data, status) VALUES (%s, %s, %s)",
            (job_id, job.input_data, "QUEUED")
        )
        conn.commit()
        cur.close()
        conn.close()

        r = get_redis()
        r.rpush("job_queue", json.dumps({"job_id": job_id, "input_data": job.input_data}))
        return {"job_id": job_id, "status": "QUEUED"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/jobs")
def list_jobs():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT 50")
        jobs = cur.fetchall()
        cur.close()
        conn.close()
        return jobs
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM jobs WHERE job_id = %s", (job_id,))
        job = cur.fetchone()
        cur.close()
        conn.close()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))