#!/bin/bash
# WhatsApp Automation - Web Dashboard Launcher

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║     🤖 WhatsApp Automation - Web Dashboard                  ║"
echo "║                                                               ║"
echo "║     🌐 Opening in Chrome automatically...                    ║"
echo "║                                                               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python not found! Please install Python first."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install fastapi uvicorn jinja2 python-telegram-bot groq requests > /dev/null 2>&1

# Start dashboard
echo ""
echo "🌐 Starting Dashboard..."
echo ""
echo "   Open your browser and go to:"
echo ""
echo "   👉 http://localhost:8500"
echo ""
echo "   (Chrome will open automatically)"
echo ""
echo "─────────────────────────────────────────────────────────"
echo ""

# Open Chrome and start server
python3 web_dashboard.py &
sleep 2

# Try to open browser
if command -v google-chrome &> /dev/null; then
    google-chrome http://localhost:8500 2>/dev/null
elif command -v chromium &> /dev/null; then
    chromium http://localhost:8500 2>/dev/null
elif command -v open &> /dev/null; then
    open http://localhost:8500 2>/dev/null
fi

wait
