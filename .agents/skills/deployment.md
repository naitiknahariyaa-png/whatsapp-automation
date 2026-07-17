# Deployment Skill

## Purpose
Deploy WhatsApp bot to production servers.

---

## Local Deployment (Windows/Mac/Linux)

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run
```bash
python main.py
```

---

## VPS/Server Deployment (Linux)

### 1. Connect to Server
```bash
ssh user@your-server-ip
```

### 2. Install Dependencies
```bash
sudo apt update
sudo apt install python3 python3-pip
sudo apt install chromium-browser  # For WhatsApp Web
```

### 3. Clone & Setup
```bash
git clone https://github.com/naitiknahariyaa-png/whatsapp-automation.git
cd whatsapp-automation
pip install -r requirements.txt
```

### 4. Configure
```bash
nano .env  # Add your API keys
```

### 5. Run with Screen
```bash
screen -S whatsapp-bot
python main.py
# Press Ctrl+A, then D to detach
```

### 6. Check Bot Status
```bash
screen -r whatsapp-bot  # Reattach
```

---

## systemd Service (Production)

### Create Service File
```bash
sudo nano /etc/systemd/system/whatsapp-bot.service
```

### Service Content
```ini
[Unit]
Description=WhatsApp AI Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/whatsapp-automation
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable whatsapp-bot
sudo systemctl start whatsapp-bot
```

### Check Status
```bash
sudo systemctl status whatsapp-bot
```

---

## Auto-Restart with Watchdog

The bot includes watchdog.py for auto-recovery:

### Run Watchdog
```bash
python watchdog.py
```

### Watchdog Checks
- Health endpoint: `http://localhost:8000/health`
- Restarts service if bot crashes
- Sends Telegram alert

---

## Docker Deployment

### Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

### Build & Run
```bash
docker build -t whatsapp-bot .
docker run -d whatsapp-bot
```

---

## Cloud Deployment

### Railway
1. Go to railway.app
2. Connect GitHub repo
3. Add environment variables
4. Deploy!

### Render
1. Go to render.com
2. Connect GitHub repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python main.py`
5. Add environment variables

### Heroku
1. Install Heroku CLI
2. `heroku create whatsapp-bot`
3. `git push heroku main`
4. Set environment variables in dashboard

---

## Environment Variables

Required for production:
```
OPENROUTER_API_KEY=xxx
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx
```

Optional:
```
DATABASE_URL=data/whatsapp.db
API_PORT=8000
LOG_LEVEL=INFO
```

---

## Health Check Endpoint

When running API server:
```
GET http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "uptime": 3600,
  "messages_processed": 150
}
```

---

## Monitoring

### Telegram Alerts
- Bot sends alerts on crashes
- Check TELEGRAM_BOT_TOKEN is set

### Logs
```bash
# View logs
tail -f logs/whatsapp-bot.log

# Or use systemd
sudo journalctl -u whatsapp-bot -f
```

---

## Security Checklist

- [ ] API keys in `.env` (not committed)
- [ ] `.env` in `.gitignore`
- [ ] HTTPS for production
- [ ] Firewall blocks unused ports
- [ ] Regular backups of `data/` folder
