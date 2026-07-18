# WhatsApp Bot Dockerfile
# Multi-stage build for smaller image

FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set Chrome environment
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set Chrome environment
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p /app/data /app/logs

# Install Playwright browsers (if needed)
RUN pip install playwright && playwright install chromium || true

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=5m --timeout=30s --start-period=10m --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the bot
CMD ["python", "main.py"]
