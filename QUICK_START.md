# 🚀 WHATSAPP AI BOT v2.0 - QUICK START

## ⚡ SUPER FAST SETUP (5 Minutes!)

### Step 1: Download & Install (2 minutes)

```bash
# Clone the project
git clone https://github.com/naitiknahariyaa-png/whatsapp-automation.git
cd whatsapp-automation

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Setup WhatsApp Session (1 minute - DO ONCE!)

```bash
python main.py
# Select option [2] to scan QR code
# Scan QR ONCE
# Session is saved - never scan again!
```

### Step 3: Setup Fast AI (2 minutes - RECOMMENDED)

```bash
# Option A: Get FREE Groq API Key (FASTEST!)
# 1. Go to: https://console.groq.com/keys
# 2. Sign up (FREE with Google/GitHub)
# 3. Create API key
# 4. Copy the key

# Option B: Use Simple Keyword AI (NO API NEEDED!)
# Just works without any setup!
```

### Step 4: Start Auto-Reply! 🚀

```bash
python main.py
# Select option [1]
# Bot is now LIVE!
```

---

## 📱 HOW IT WORKS

### Session Persistence (Login Once!)
```
┌─────────────────────────────────────────┐
│  First Time:                           │
│  1. Run python main.py                 │
│  2. Select [2] Setup Session           │
│  3. Scan QR code with WhatsApp         │
│  4. Done! Session is saved!            │
├─────────────────────────────────────────┤
│  Next Time:                            │
│  1. Run python main.py                 │
│  2. Select [1] Start Bot               │
│  3. Bot starts automatically!          │
│  4. No QR scanning needed!             │
└─────────────────────────────────────────┘
```

### Auto-Reply Flow
```
📱 Customer sends message
    ↓
🤖 Bot receives message
    ↓
📝 Check keywords OR ask AI
    ↓
💬 Generate response
    ↓
📤 Send auto-reply
    ↓
✅ Customer gets instant reply!
```

---

## 🤖 AI OPTIONS (Choose One!)

### Option A: Groq AI ⭐ RECOMMENDED
**Speed: 10x FASTER than Ollama!**
**Cost: FREE (30 requests/minute)**

1. Go to: https://console.groq.com/keys
2. Sign up FREE
3. Get API key
4. Enter in menu option [3]

### Option B: Simple Keyword AI ✅
**Speed: INSTANT (No AI needed!)**
**Cost: FREE (No API key!)**

Just works! Add your own keywords:
- "hi" → "Hello!"
- "price" → "Our prices are..."
- Any custom keywords you want!

---

## 📋 MENU OPTIONS

```
[1] 🚀 Start Auto-Reply Bot    ← Start monitoring messages
[2] 📱 Setup WhatsApp Session   ← Scan QR once (do first time)
[3] 🤖 Set Up Groq AI          ← Set up FREE fast AI
[4] 📝 Add Keywords            ← Add custom auto-reply keywords
[5] 📊 View Statistics         ← See messages & replies count
[6] 💬 Test Auto-Reply         ← Test without WhatsApp
[7] ⚙️  Settings               ← View current settings
[8] 🗑️  Clear All Data         ← Reset everything
[0] Exit
```

---

## 💬 EXAMPLE CONVERSATIONS

### With Groq AI (Smart Responses)
```
Customer: "Hi, what are your prices?"
Bot: "Hello! Our prices start from ₹499. Which product are you interested in?"

Customer: "Do you deliver to Mumbai?"
Bot: "Yes! We deliver all over India. Delivery takes 3-5 business days."
```

### With Keyword AI (Your Custom Keywords)
```
Customer: "What are your hours?"
Bot: "We're open 9 AM to 9 PM, all days! 🌟"

Customer: "Where are you located?"
Bot: "We're at [Your Address]. You can find us on Google Maps! 📍"
```

---

## ⚙️ CUSTOMIZATION

### Add Your Own Keywords
```bash
# Run main.py, select [4]
Enter keyword: pizza
Enter response: "We have Margherita, Pepperoni, and Supreme! Which one would you like? 🍕"

# Now when someone says "pizza", bot replies automatically!
```

### Set Business Info
Edit the responses in `main.py`:
```python
self.defaults = {
    "location": "We're at YOUR ADDRESS HERE",
    "contact": "Call us: YOUR PHONE NUMBER",
    "hours": "Open YOUR HOURS here",
}
```

---

## 🔧 TROUBLESHOOTING

### QR Code Not Working?
```bash
# Make sure:
1. Chrome is installed
2. Internet is connected
3. WhatsApp is linked to phone
```

### Bot Not Responding?
```bash
# Check:
1. Is bot running? (option [1])
2. Are there unread messages?
3. Is WhatsApp Web open in Chrome?
```

### Groq API Not Working?
```bash
# Make sure:
1. API key is correct
2. Key is not expired
3. You have internet connection
```

---

## 📊 WHAT'S SAVED

```
data/
├── whatsapp.db          ← Messages & keywords
└── session/
    └── backup_session/  ← WhatsApp session (NEVER scan QR again!)
```

---

## 🎯 NEXT STEPS FOR BUSINESS

1. ✅ Set up bot (5 minutes)
2. ✅ Add your business keywords
3. ✅ Set up Groq AI for smart replies
4. ✅ Start getting clients!

### Pricing Strategy
- WhatsApp Auto-Reply Setup: ₹2,999 one-time
- Monthly Maintenance: ₹999/month
- Target: Small shops, restaurants, clinics

---

## 🆘 NEED HELP?

- WhatsApp Web automation: https://web.whatsapp.com
- Groq API: https://console.groq.com
- Selenium: https://www.selenium.dev

---

**Built for Indian Businesses 🇮🇳**
**Made with ❤️**
