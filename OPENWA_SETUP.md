# OpenWA Setup Guide - Complete Step-by-Step

## What is OpenWA?

**OpenWA** is a free, open-source WhatsApp API Gateway with:
- 11.4k GitHub stars
- REST API for WhatsApp
- Multi-session support
- Web Dashboard
- Webhooks
- MCP Server for AI agents
- Docker native

---

## Option 1: Without Docker (Node.js)

### Step 1: Install Node.js

1. Go to: https://nodejs.org
2. Download **LTS** version (v22.x)
3. Install it
4. Restart your PC

### Step 2: Verify Node.js

```powershell
# Open PowerShell and run:
node --version
npm --version
```

Should show:
```
v22.x.x
10.x.x
```

### Step 3: Clone OpenWA

```powershell
cd C:\
git clone https://github.com/rmyndharis/OpenWA.git
cd OpenWA
```

### Step 4: Install Dependencies

```powershell
npm install
```

### Step 5: Start OpenWA

```powershell
npm run dev
```

### Step 6: Access OpenWA

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:2886 |
| API | http://localhost:2785/api |
| Swagger Docs | http://localhost:2785/api/docs |

---

## Option 2: With Docker

### Step 1: Enable WSL

Run **PowerShell as Administrator**:

```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

### Step 2: Restart PC

```powershell
shutdown /r /t 0
```

### Step 3: Install Docker Desktop

1. Download from: https://www.docker.com/products/docker-desktop
2. Install and start Docker Desktop
3. Wait until "Docker Desktop is running"

### Step 4: Clone and Start

```powershell
cd C:\
git clone https://github.com/rmyndharis/OpenWA.git
cd OpenWA
docker compose -f docker-compose.dev.yml up -d
```

### Step 5: Access

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:2785 |
| API | http://localhost:2785/api |
| Swagger | http://localhost:2785/api/docs |

---

## Option 3: Use Cloud Version

### No Installation Needed!

1. Go to: https://open-wa.org
2. Sign up for free
3. Get your API URL and Key
4. Add to your bot's `.env`

---

## Connect to Your WhatsApp Bot

### Step 1: Get API Key from OpenWA Dashboard

1. Open: http://localhost:2785
2. Go to **Settings** → **API Keys**
3. Click **Create New Key**
4. Copy the key

### Step 2: Add to Your Bot's `.env`

```env
OPENWA_URL=http://localhost:2785
OPENWA_API_KEY=your-api-key-here
OPENWA_SESSION_ID=default
```

### Step 3: Pull Latest Code

```powershell
cd C:\Users\PC\whatsapp-automation
git pull origin main
```

### Step 4: Test Connection

```powershell
python -c "from src.integrations import OpenWAGateway; g=OpenWAGateway(); print('OpenWA:', 'Connected!' if g.enabled else 'Not configured')"
```

---

## API Usage Examples

### Create Session
```powershell
curl -X POST http://localhost:2785/api/sessions `
  -H "Content-Type: application/json" `
  -H "X-API-Key: YOUR_API_KEY" `
  -d '{"name": "my-bot"}'
```

### Start Session
```powershell
curl -X POST http://localhost:2785/api/sessions/my-bot/start `
  -H "X-API-Key: YOUR_API_KEY"
```

### Get QR Code
```powershell
curl http://localhost:2785/api/sessions/my-bot/qr `
  -H "X-API-Key: YOUR_API_KEY"
```

### Send Message
```powershell
curl -X POST http://localhost:2785/api/sessions/my-bot/messages/send-text `
  -H "Content-Type: application/json" `
  -H "X-API-Key: YOUR_API_KEY" `
  -d '{"chatId": "919876543210@c.us", "text": "Hello from OpenWA!"}'
```

---

## Python Integration

```python
from src.integrations import OpenWAGateway

# Initialize
gateway = OpenWAGateway()

# Create session
gateway.create_session("my-bot")

# Start session
gateway.start_session("my-bot")

# Send message
gateway.send_text("919876543210@c.us", "Hello!")

# Send bulk messages
gateway.send_bulk_messages(
    numbers=["919876543210@c.us", "919876543211@c.us"],
    message="Hello everyone!"
)
```

---

## Troubleshooting

### Port Already in Use

```powershell
# Find what's using port 2785
netstat -ano | findstr 2785

# Kill the process
taskkill /PID <PID_NUMBER> /F
```

### npm install fails

```powershell
# Clear npm cache
npm cache clean --force

# Try again
npm install
```

### Docker not starting

1. Enable WSL features (see Option 2)
2. Restart PC
3. Start Docker Desktop
4. Wait 2 minutes

---

## Links

| Resource | URL |
|----------|-----|
| OpenWA GitHub | https://github.com/rmyndharis/OpenWA |
| Documentation | https://github.com/rmyndharis/OpenWA#readme |
| OpenWA Cloud | https://open-wa.org |
| Node.js | https://nodejs.org |
| Docker Desktop | https://www.docker.com/products/docker-desktop |

---

## Next Steps

1. ✅ Follow this guide
2. ✅ Start OpenWA
3. ✅ Get API Key
4. ✅ Add to your bot's `.env`
5. ✅ Test sending a message

Good luck! 🚀
