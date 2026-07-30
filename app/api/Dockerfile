# Stage 1: Build dependencies
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final minimal runtime
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl && rm -rf /var/lib/apt/lists/*
COPY --from=builder /install /usr/local
COPY main.py .

RUN useradd -u 10001 appuser && chown -R appuser:appuser /app
USER 10001

EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --retries=3 CMD curl -f http://localhost:8000/health/live || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]