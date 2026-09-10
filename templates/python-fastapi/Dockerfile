# syntax=docker/dockerfile:1.6
# Backend image for a FastAPI service. Copy to backend/Dockerfile.
# Two stages: deps into a venv, then a slim non-root runtime with a healthcheck.
# App Platform reads EXPOSE/http_port from the spec, not from here.

FROM python:3.12-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/opt/venv/bin:$PATH" \
    ENVIRONMENT=production PORT=8000
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 app
COPY --from=builder /opt/venv /opt/venv
WORKDIR /app
COPY . /app
RUN mkdir -p /app/data && chown -R app:app /app
USER app
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${PORT}/health" || exit 1
EXPOSE 8000
# Run migrations (if alembic is present) then serve. Keep workers at 1 on the
# smallest instance; raise once a Postgres connection pool is in place.
CMD ["sh", "-c", "([ -d alembic ] && alembic upgrade head || true) && uvicorn src.main:app --host 0.0.0.0 --port ${PORT} --workers 1"]
