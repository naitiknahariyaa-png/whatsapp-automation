@echo off
title WhatsApp Automation Hub
color 0A
cd /d "%~dp0"

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║       🤖 WhatsApp Automation - Auto Start                  ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Install from https://python.org
    pause
    exit /b 1
)

:: Check Docker
docker info >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker not running. Starting Docker Desktop...
    start docker
    echo ⏱️  Waiting 30s for Docker to start...
    timeout /t 30 /nobreak >nul
)

echo.
echo 🚀 Starting WhatsApp Automation Hub...
echo.

:: Install dependencies if needed
pip install -q -r requirements.txt 2>nul

:: Start the auto-launcher
echo 📦 Starting all services automatically...
python auto_start_launcher.py --background

echo.
echo ✅ WhatsApp Automation Hub is running in background!
echo.
echo 🌐 Access URLs:
echo    - Hub: Check the running window
echo    - OpenWA: http://localhost:2785
echo    - N8N: http://localhost:5678
echo.
echo 💡 Check auto_start.log for logs
echo.
echo Press any key to open logs folder...
pause >nul
explorer "%~dp0data"

:: Minimize to tray (optional)
cmd /c start /min cmd /c "python auto_start_launcher.py --background"
