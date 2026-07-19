#!/bin/bash
# Stop WhatsApp Bot Daemon

echo "Stopping WhatsApp Bot..."

# Stop dashboard
if [ -f .bot_pid ]; then
    PID=$(cat .bot_pid)
    kill $PID 2>/dev/null
    echo "✅ Dashboard stopped (PID: $PID)"
    rm .bot_pid
fi

# Stop OpenWA
docker stop openwa 2>/dev/null
docker rm openwa 2>/dev/null
echo "✅ OpenWA stopped"

echo ""
echo "All services stopped!"
