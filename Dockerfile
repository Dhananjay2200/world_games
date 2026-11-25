# =====================================================================
# WorldGames AI - High-Throughput Production Dockerfile
# Multi-worker async architecture with Gunicorn & Uvicorn workers
# =====================================================================

FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt
RUN pip install --no-cache-dir --user gunicorn cachetools uvloop httptools

# Final Stage
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy backend application and compiled frontend bundle
COPY app/ app/
COPY frontend/dist/ frontend/dist/
COPY .env.example .env

ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production
ENV DEBUG=false
ENV PORT=8001

EXPOSE 8001

# High-concurrency Gunicorn runner with async Uvicorn workers
# Formula: 2-4 workers per CPU core, uvloop high-speed event loop
CMD ["gunicorn", "app.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8001", \
     "--timeout", "120", \
     "--keep-alive", "65", \
     "--backlog", "4096", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
