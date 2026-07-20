---
name: docker-deployment
description: Docker containerization for WhatsApp Automation Hub including multi-service setup with OpenWA, Redis, and Nginx. Use for production deployment, scaling, or development environment setup.
trigger phrases: ["docker", "container", "deployment", "docker-compose", "production"]
tags: [docker, deployment, container, production, scaling]
complexity: medium
cost: free
self-hosted: true
---

# Docker Deployment Skill

## Overview

Deploy WhatsApp Hub with Docker for production reliability.

## Docker Compose Setup

```yaml
version: '3.8'
services:
  # Main App
  whatsapp-hub:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENWA_URL=http://openwa:3000
      - OPENWA_API_KEY=${OPENWA_API_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ./data:/app/data
    depends_on:
      - openwa

  # WhatsApp Gateway
  openwa:
    image: waha/waha:latest
    ports:
      - "3000:3000"
    volumes:
      - openwa_data:/data

  # Redis Cache (optional)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  openwa_data:
  redis_data:
```

## Build & Run

```bash
# Build image
docker build -t whatsapp-hub .

# Run with env file
docker run -d \
  --name whatsapp-hub \
  -p 8000:8000 \
  --env-file .env \
  whatsapp-hub
```

## Production Tips

1. **Use Docker Compose** for multi-service
2. **Set environment variables** in `.env`
3. **Use volumes** for data persistence
4. **Set resource limits** for memory/CPU
5. **Enable healthchecks** for monitoring

## Common Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Rebuild
docker-compose up -d --build
```

## Resource Limits

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
```
