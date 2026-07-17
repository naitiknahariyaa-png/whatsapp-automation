# PM2 Auto-Healing Skill

## Purpose
Use PM2 for process management with auto-restart.

## What is PM2?
Production process manager with auto-restart and clustering.

## Setup

### 1. Install PM2
```bash
npm install -g pm2

# Or for Python bot
pip install pm2
pm2 install pm2-python-watch
```

### 2. Start Bot with PM2
```bash
# Start Python script
pm2 start main.py --name whatsapp-bot

# Start with auto-restart
pm2 start main.py --name whatsapp-bot --watch

# Start with environment
pm2 start main.py --name whatsapp-bot --env production
```

### 3. Auto-Healing Config
```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: "whatsapp-bot",
    script: "main.py",
    interpreter: "python3",
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: "1G",
    env: {
      NODE_ENV: "production"
    },
    // Auto-healing settings
    exp_backoff_restart_delay: 100,
    max_restarts: 10,
    min_uptime: "10s"
  }]
}
```

## Commands

| Command | Description |
|---------|-------------|
| `pm2 start main.py` | Start bot |
| `pm2 stop whatsapp-bot` | Stop bot |
| `pm2 restart whatsapp-bot` | Restart bot |
| `pm2 logs whatsapp-bot` | View logs |
| `pm2 monit` | Monitor CPU/RAM |
| `pm2 status` | Check status |
| `pm2 delete whatsapp-bot` | Remove from PM2 |

## Auto-Healing Features

```bash
# Enable auto-restart on crash
pm2 update --restart-delay 100

# Watch for file changes
pm2 start main.py --watch

# Memory limit auto-restart
pm2 start main.py --max-memory-restart 1G

# Auto-start on system boot
pm2 startup
pm2 save
```

## Monitoring
```bash
# Real-time dashboard
pm2 monit

# Check logs
pm2 logs whatsapp-bot --lines 100

# Check detailed status
pm2 show whatsapp-bot
```

## Environment Variables
```bash
# Set env vars
pm2 start main.py --env production

# Or in ecosystem file
env: {
  OPENAI_API_KEY: "xxx",
  TELEGRAM_TOKEN: "xxx"
}
```

## Clustering (Scale to 10k users)
```bash
# Scale to 4 instances
pm2 scale whatsapp-bot 4

# Load balance across cores
pm2 start main.py -i max
```

## System Boot
```bash
# Generate startup script
pm2 startup

# Save current state
pm2 save

# Now bot auto-starts on reboot
```

## More Info
- Website: https://pm2.keymetrics.io
- GitHub: https://github.com/Unitech/pm2
