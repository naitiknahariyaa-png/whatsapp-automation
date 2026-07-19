@echo off
title WhatsApp Automation Dashboard
color 0A
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                                                               ║
echo  ║     🤖 WhatsApp Automation - Web Dashboard                  ║
echo  ║                                                               ║
echo  ║     🌐 Opening in Chrome automatically...                    ║
echo  ║                                                               ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python first.
    echo Download: https://python.org/downloads
    pause
    exit
)

REM Install dependencies if needed
echo 📦 Checking dependencies...
pip install fastapi uvicorn jinja2 python-telegram-bot groq requests >nul 2>&1

REM Start the web dashboard
echo.
echo 🌐 Starting Dashboard...
echo.
echo    Open your browser and go to:
echo.
echo    👉 http://localhost:8500
echo.
echo    (Chrome will open automatically)
echo.
echo ─────────────────────────────────────────────────────────
echo.

REM Start dashboard and open Chrome
start http://localhost:8500
python web_dashboard.py

pause
