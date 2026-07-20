# 📦 NEXUS - Super Simple Install Guide (Baby Steps)

## 🎯 What You Need First

### On Your Computer:
1. **Node.js 20+** - Download from https://nodejs.org (click the big green button)
2. **VS Code** - Download from https://code.visualstudio.com (free code editor)

### Get These Free Accounts:
1. **OpenAI API Key** - Go to https://platform.openai.com → Sign up → API Keys
2. **Telegram Bot Token** - Open Telegram → Search @BotFather → Send `/newbot`
3. **GitHub Token** - Go to https://github.com → Settings → Developer settings → Personal access tokens

---

## 🟢 STEP 1: Download the Code (Baby Step)

Open your computer's **Terminal** (Mac) or **Command Prompt** (Windows):

```bash
# Go to where you keep projects
cd ~/Desktop

# Download the code
git clone https://github.com/naitiknahariyaa-png/whatsapp-automation.git

# Go into the NEXUS folder
cd whatsapp-automation/nexus
```

---

## 🟢 STEP 2: Install Everything (Baby Step)

Still in the terminal:

```bash
# This installs all the code (wait 2-5 minutes)
npm install
```

---

## 🟢 STEP 3: Setup Settings (Baby Step)

```bash
# Create a settings file
cp .env.example .env
```

Now open `.env` file in VS Code and fill in your info:

```
OPENAI_API_KEY=sk-your-key-here
TELEGRAM_BOT_TOKEN=123456:ABC-YourToken
GITHUB_TOKEN=ghp_yourGitHubToken
PORT=3000
```

---

## 🟢 STEP 4: Start the App! (Baby Step)

```bash
# Start the app!
npm run dev
```

You should see:
```
🚀 NEXUS Platform v3.0 starting...
✅ All systems ready!
🌐 Server running at http://localhost:3000
```

---

## 🟢 STEP 5: Open in Browser

1. Open **Chrome** or **Firefox**
2. Go to: **http://localhost:3000**
3. You'll see NEXUS dashboard! 🎉

---

## 📱 Connect WhatsApp (Baby Step)

1. Open **Telegram**
2. Find your bot (the one you created with BotFather)
3. Send `/start`
4. Send `/connect`
5. Scan the QR code with your WhatsApp phone

---

## 💬 Use Telegram Commands

In your Telegram bot, try these:

| Command | What It Does |
|---------|-------------|
| `/start` | Start the bot |
| `/help` | See all commands |
| `/status` | Check NEXUS status |
| `/stats` | See analytics |

---

## 🔌 API Testing (Optional)

Test the API with curl:

```bash
# Check if NEXUS is running
curl http://localhost:3000/health

# Send a chat message
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello NEXUS!"}'
```

---

## 🐳 Install with Docker (Advanced)

If you have Docker installed:

```bash
# Start everything
docker-compose up -d

# Check if running
docker-compose ps
```

---

## ❓ Troubleshooting

### "npm not found"
→ Install Node.js from https://nodejs.org

### "Port 3000 is busy"
→ Change port in `.env`: `PORT=3001`

### "WhatsApp not connecting"
→ Make sure you scan QR within 60 seconds
→ Try `/disconnect` then `/connect` again

### "AI not responding"
→ Check your OPENAI_API_KEY is correct
→ Make sure you have credits at https://platform.openai.com

---

## 🎉 You're Done!

```
╔═══════════════════════════════════════╗
║                                       ║
║   🎉 NEXUS IS NOW RUNNING! 🎉        ║
║                                       ║
║   🌐 Dashboard: localhost:3000        ║
║   💬 Telegram: Your bot               ║
║   📱 WhatsApp: Scan QR to connect     ║
║                                       ║
╚═══════════════════════════════════════╝
```

---

## 📞 Need Help?

1. **GitHub Issues**: https://github.com/naitiknahariyaa-png/whatsapp-automation/issues
2. **PR**: https://github.com/naitiknahariyaa-png/whatsapp-automation/pull/4

**Happy Automating!** 🚀

---

*Made with ❤️ by NEXUS*
