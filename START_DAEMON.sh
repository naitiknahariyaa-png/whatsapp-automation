#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# WhatsApp Bot - Background Daemon Setup
# ═══════════════════════════════════════════════════════════════════════
# 
# This script starts everything in background:
# 1. OpenWA Gateway (WhatsApp)
# 2. Web Dashboard
#
# Usage: ./start_daemon.sh
# ═══════════════════════════════════════════════════════════════════════

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║     🤖 WhatsApp Bot - Daemon Launcher                       ║"
echo "║                                                               ║"
echo "║     Everything runs in background!                           ║"
echo "║                                                               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found!${NC}"
    echo ""
    echo "Please install Docker first:"
    echo "  → https://docker.com/products/docker-desktop"
    echo ""
    echo "After installing, run this script again."
    exit 1
fi

echo -e "${GREEN}✅ Docker found${NC}"

# ═══════════════════════════════════════════════════════════════════════
# STEP 1: Stop existing containers
# ═══════════════════════════════════════════════════════════════════════

echo ""
echo "─────────────────────────────────────────────────────────────"
echo "STEP 1: Cleaning up old processes..."
echo "─────────────────────────────────────────────────────────────"

docker stop openwa 2>/dev/null
docker rm openwa 2>/dev/null
echo "✅ Cleaned up"

# ═══════════════════════════════════════════════════════════════════════
# STEP 2: Start OpenWA Gateway
# ═══════════════════════════════════════════════════════════════════════

echo ""
echo "─────────────────────────────────────────────────────────────"
echo "STEP 2: Starting WhatsApp Gateway (OpenWA)..."
echo "─────────────────────────────────────────────────────────────"
echo ""

docker run -d \
    --name openwa \
    -p 3000:3000 \
    -p 3001:3001 \
    -e AUTH_KEY=owa_k1_6bba1f24ebb42e3e22af75bd8c1d503ec003a33d1ec9d4f8e3d00872f5586ec9 \
    -e SESSION=default \
    --restart unless-stopped \
    waha/waha:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ OpenWA container started!${NC}"
else
    echo -e "${RED}❌ Failed to start OpenWA${NC}"
    echo "Container may already be running. Checking..."
    docker ps -a | grep openwa
fi

# ═══════════════════════════════════════════════════════════════════════
# STEP 3: Install Python dependencies
# ═══════════════════════════════════════════════════════════════════════

echo ""
echo "─────────────────────────────────────────────────────────────"
echo "STEP 3: Installing Python dependencies..."
echo "─────────────────────────────────────────────────────────────"
echo ""

pip install fastapi uvicorn jinja2 groq requests python-dotenv -q 2>/dev/null

echo -e "${GREEN}✅ Dependencies installed${NC}"

# ═══════════════════════════════════════════════════════════════════════
# STEP 4: Start Web Dashboard
# ═══════════════════════════════════════════════════════════════════════

echo ""
echo "─────────────────────────────────────────────────────────────"
echo "STEP 4: Starting Web Dashboard..."
echo "─────────────────────────────────────────────────────────────"
echo ""

# Start dashboard in background
nohup python web_dashboard.py > bot.log 2>&1 &
DASHBOARD_PID=$!

echo -e "${GREEN}✅ Dashboard started (PID: $DASHBOARD_PID)${NC}"

# ═══════════════════════════════════════════════════════════════════════
# STEP 5: Save PIDs for later management
# ═══════════════════════════════════════════════════════════════════════

echo $DASHBOARD_PID > .bot_pid
echo "Dashboard PID saved to .bot_pid"

# ═══════════════════════════════════════════════════════════════════════
# DONE
# ═══════════════════════════════════════════════════════════════════════

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║     🎉 ALL SERVICES STARTED!                                ║"
echo "║                                                               ║"
echo "║     📱 WhatsApp Gateway: http://localhost:3000              ║"
echo "║     🌐 Web Dashboard:      http://localhost:8500           ║"
echo "║     📊 Logs:               ./bot.log                      ║"
echo "║                                                               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "NEXT STEPS:"
echo "1. Open: http://localhost:3000"
echo "2. Scan QR code with WhatsApp"
echo "3. Done! WhatsApp will auto-reply!"
echo ""
echo "TO STOP:"
echo "  ./stop_daemon.sh"
echo ""
