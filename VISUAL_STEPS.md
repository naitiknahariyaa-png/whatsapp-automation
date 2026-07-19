# 📋 STEP BY STEP - WhatsApp Automation Setup

## 🟢 STEP 1: Install Docker (First Time Only)

**Time: 10 minutes**

```
1. Open browser → Go to: https://docker.com/products/docker-desktop

2. Click green "Download Docker Desktop" button

3. Double-click downloaded file to install

4. Wait 5 minutes for installation

5. Search "Docker Desktop" in Start Menu and open it

6. Wait until you see "Docker Desktop is running" in bottom right
```

---

## 🔵 STEP 2: Start WhatsApp Gateway

**Time: 5 minutes (first time), 30 seconds (after)**

**Open Command Prompt:**
- Press `Windows Key + R`
- Type `cmd`
- Press `Enter`

**Copy and paste this command:**
```bash
docker run -d --name openwa -p 3000:3000 waha/waha:latest
```

**Press Enter and wait 5 minutes**

---

## 🟡 STEP 3: Connect WhatsApp

**Time: 2 minutes**

```
1. Open Chrome browser

2. Type: http://localhost:3000
   (Press Enter)

3. Click "Connect WhatsApp" button

4. Open WhatsApp on your phone:
   📱 iPhone: Settings → Linked Devices → Link a Device
   📱 Android: ⋮ Menu → Linked Devices → Link a Device

5. Scan the QR code on screen

6. ✅ Done! WhatsApp connected!
```

---

## 🟠 STEP 4: Start Dashboard

**Time: 30 seconds**

**Open Command Prompt (if closed):**
- Press `Windows Key + R`
- Type `cmd`
- Press `Enter`

**Type these commands:**
```bash
cd whatsapp-automation
python web_dashboard.py
```

**You'll see:**
```
🌐 Open your browser and go to:
👉 http://localhost:8500
```

**Press Ctrl + Click the link OR open Chrome and type: http://localhost:8500**

---

## 🔴 STEP 5: Use Your Dashboard!

### 📊 Add Customers:
```
1. Click "Customers" tab
2. Enter phone: 919876543210
3. Click "Add Customer"
```

### 📝 Set Auto-Replies:
```
1. Click "Templates" tab
2. Keyword: hello
3. Response: Hi! Welcome!
4. Click "Add Template"
```

### 📢 Send to All:
```
1. Click "Broadcast" tab
2. Type your message
3. Click "Send to All Customers"
```

---

## ⭐ QUICK START COMMANDS

| What | Command |
|------|---------|
| Start Dashboard | `cd whatsapp-automation` then `python web_dashboard.py` |
| Open Dashboard | Chrome → http://localhost:8500 |
| Open WhatsApp | Chrome → http://localhost:3000 |
| Stop Dashboard | Press `Ctrl + C` in Command Prompt |

---

## ❓ IF SOMETHING GOES WRONG

### Docker not starting?
```
1. Restart Docker Desktop app
2. Wait 1 minute
3. Try again
```

### WhatsApp not connecting?
```
1. Go to http://localhost:3000
2. Click your profile → Logout
3. Re-scan QR code
```

### Dashboard shows error?
```
1. Make sure Command Prompt is running python web_dashboard.py
2. Refresh Chrome page
3. If still error, restart Step 4
```

---

## 🎉 YOU'RE DONE!

Now you have:
- ✅ WhatsApp auto-replies
- ✅ Customer management
- ✅ Broadcast to all
- ✅ Beautiful dashboard
- ✅ AI-powered responses

**Dashboard is at: http://localhost:8500**
