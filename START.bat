@echo off
echo ====================================
echo   WhatsApp AI Bot - Starting...
echo ====================================

REM Delete old database if exists
if exist "data\whatsapp.db" del /q "data\whatsapp.db"
if exist "data\bot.db" del /q "data\bot.db"

REM Create data folder if not exists
if not exist "data" mkdir data

REM Install dependencies if needed
pip install -r requirements.txt

REM Run the bot
python main.py

pause
