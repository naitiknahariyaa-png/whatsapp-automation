@echo off
title WhatsApp Automation - Docker Setup
color 0A

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║       📦 Docker Container Setup (Run Once)                ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

echo ⏱️  This will download images (first time only - takes time!)
echo.

:: Redis
echo [1/5] Setting up Redis...
docker run -d --name redis -p 6379:6379 redis:alpine

:: PostgreSQL
echo [2/5] Setting up PostgreSQL...
docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=whatsapp_bot postgres:15

:: OpenWA
echo [3/5] Setting up OpenWA (WhatsApp Gateway)...
docker run -d --name openwa -p 2785:3000 -p 8181:8181 waha/e2e-js:latest

:: N8N
echo [4/5] Setting up N8N Automation...
docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n

:: MinIO
echo [5/5] Setting up MinIO Storage...
docker run -d --name minio -p 9000:9000 -p 9001:9001 -e MINIO_ROOT_USER=minioadmin -e MINIO_ROOT_PASSWORD=minioadmin minio/minio server /data --console-address ":9001"

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║       ✅ Setup Complete!                                ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
echo Now run: python quick_start.py
echo.
pause
