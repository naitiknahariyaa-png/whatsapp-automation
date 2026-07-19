# 📱 WhatsApp + Telegram Connection Guide

## Your Current Status

| Component | Status |
|-----------|--------|
| ✅ Telegram Bot | Working - @whatsappuubot |
| ✅ Groq AI | Connected |
| ❌ WhatsApp | Needs OpenWA setup |

---

## 🔗 How It Works

```
WhatsApp User → OpenWA → Your Bot → AI → Reply
                    ↓
              Telegram Alert (Admin)
```

---

## 🚀 Step 1: Start OpenWA (On Your Computer)

### Option A: Using Docker (Recommended)

```bash
# Run this command on your computer:
docker run -d --name openwa -p 3000:3000 waha/waha:latest
```

Wait 2-5 minutes for download and startup.

### Option B: Without Docker - Use Cloud

1. Go to: https://open-wa.org
2. Sign up for free account
3. Get your API URL and Key
4. Update `.env` file

---

## 🔑 Step 2: Configure OpenWA API

Once OpenWA is running, update your `.env`:

```env
OPENWA_URL=http://localhost:3000
OPENWA_API_KEY=owa_k1_6bba1f24ebb42e3e22af75bd8c1d503ec003a33d1ec9d4f8e3d00872f5586ec9
OPENWA_SESSION_ID=046a8e1e-51fe-4dbc-8351-2ac838e4f2fa
```

---

## 📱 Step 3: Connect WhatsApp

1. Open browser: http://localhost:3000
2. Click "Connect WhatsApp"
3. Scan QR code with your phone
4. Your WhatsApp is now connected!

---

## 🧪 Step 4: Test Connection

```bash
# Test WhatsApp connection
python -c "
import requests
headers = {'X-API-Key': 'owa_k1_6bba1f24ebb42e3e22af75bd8c1d503ec003a33d1ec9d4f8e3d00872f5586ec9'}
r = requests.get('http://localhost:3000/api/connection', headers=headers)
print('Status:', r.status_code)
print('Connected!' if r.status_code == 200 else 'Not connected')
"
```

---

## 🤖 Step 5: Start Your Bot

```bash
python complete_bot.py
```

Now:
- ✅ WhatsApp messages → Auto-replied by AI
- ✅ Telegram → Control panel for you
- ✅ Broadcast → Send to all WhatsApp contacts

---

## ⚠️ If Docker Won't Start

### Windows:
1. Install Docker Desktop: https://docker.com/products/docker-desktop
2. Start Docker Desktop
3. Wait until "Docker is running"

### Linux:
```bash
sudo systemctl start docker
sudo docker run -d --name openwa -p 3000:3000 waha/waha:latest
```

### Mac:
```bash
# Install Docker Desktop
open -a Docker
# Wait for Docker to start
docker run -d --name openwa -p 3000:3000 waha/waha:latest
```

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Find what's using port 3000
netstat -ano | findstr 3000

# Kill it
taskkill /PID <PID> /F
```

### OpenWA Not Loading
```bash
# Check logs
docker logs openwa

# Restart
docker restart openwa
```

### WhatsApp Session Expired
1. Delete session in OpenWA dashboard
2. Re-scan QR code

---

## 📊 Expected Results

After setup:
```
📱 WhatsApp User sends: "Hi"
    ↓
🤖 Bot receives message
    ↓
🧠 AI generates response
    ↓
📤 Bot sends reply
    ↓
📱 WhatsApp User gets instant reply!
    ↓
📢 You get Telegram notification (optional)
```

---

## 🎯 Quick Checklist

- [ ] Docker installed
- [ ] OpenWA container running
- [ ] WhatsApp scanned and connected
- [ ] `python complete_bot.py` running
- [ ] Test message sent

---

## 💡 Pro Tips

1. **Keep OpenWA Running**: Add to startup so it auto-starts
2. **Session Never Expires**: WhatsApp session stays active
3. **Monitor**: Check Telegram for incoming messages
4. **Scale**: Add more customers = more orders!

---

## 📞 Need Help?

Check OpenWA docs: https://github.com/rmyndharis/OpenWA
