@echo off
title WhatsApp Bot - Daemon Launcher
color 0A
cls

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                                                               ║
echo  ║     🤖 WhatsApp Bot - Background Launcher                   ║
echo  ║                                                               ║
echo  ║     Everything runs in background!                           ║
echo  ║                                                               ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker not found!
    echo.
    echo Please install Docker:
    echo 1. Go to: https://docker.com/products/docker-desktop
    echo 2. Download and install
    echo 3. Restart computer
    echo 4. Run this script again
    echo.
    pause
    exit
)

echo ✅ Docker found!
docker --version
echo.

echo ════════════════════════════════════════════════════════════════
echo STEP 1: Cleaning up old processes...
echo ════════════════════════════════════════════════════════════════
echo.

docker stop openwa >nul 2>&1
docker rm openwa >nul 2>&1
echo ✅ Cleaned up

echo.
echo ════════════════════════════════════════════════════════════════
echo STEP 2: Starting WhatsApp Gateway (OpenWA)...
echo ════════════════════════════════════════════════════════════════
echo.

docker run -d --name openwa -p 3000:3000 -p 3001:3001 ^
    -e AUTH_KEY=owa_k1_6bba1f24ebb42e3e22af75bd8c1d503ec003a33d1ec9d4f8e3d00872f5586ec9 ^
    -e SESSION=default --restart unless-stopped waha/waha:latest

if errorlevel 1 (
    echo ⚠️ OpenWA may already be running
    docker ps -a | findstr openwa
) else (
    echo ✅ OpenWA started!
)

echo.
echo ⏳ Wait 5 minutes for first-time download...
echo.

echo ════════════════════════════════════════════════════════════════
echo STEP 3: Installing dependencies...
echo ════════════════════════════════════════════════════════════════
echo.

pip install fastapi uvicorn jinja2 groq requests python-dotenv -q

echo ✅ Dependencies installed!

echo.
echo ════════════════════════════════════════════════════════════════
echo STEP 4: Starting Web Dashboard in background...
echo ════════════════════════════════════════════════════════════════
echo.

REM Start in background using Windows "start" command
start /B python web_dashboard.py > bot.log 2>&1

echo ✅ Dashboard started in background!
echo 📊 Logs: bot.log

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║     🎉 ALL SERVICES STARTED!                                ║
echo ║                                                               ║
echo ║     📱 WhatsApp Gateway: http://localhost:3000              ║
echo ║     🌐 Web Dashboard:      http://localhost:8500           ║
echo ║                                                               ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo NEXT STEPS:
echo 1. Open Chrome: http://localhost:3000
echo 2. Scan QR code with WhatsApp
echo 3. WhatsApp will connect!
echo.
echo TO STOP:
echo   docker stop openwa
echo   taskkill /F /IM python.exe
echo.

pause
