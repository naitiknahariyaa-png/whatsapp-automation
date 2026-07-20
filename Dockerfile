# WhatsApp Automation Hub - Production Dockerfile
# Multi-stage build for optimized image size

FROM python:3.11-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
LABEL maintainer="WhatsApp Hub"
RUN groupadd --gid 1000 appgroup && useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN apt-get update && apt-get install -y chromium chromium-driver curl && rm -rf /var/lib/apt/lists/*
COPY --chown=appuser:appgroup . .
RUN mkdir -p /app/data /app/logs && chown -R appuser:appgroup /app/data /app/logs
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app
EXPOSE 8000 3000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD curl -f http://localhost:8000/health || exit 1
USER appuser
CMD ["python", "web_dashboard.py"]
