# 📋 How to Test If Your WhatsApp Bot Is Talking

## 🚨 Important: You Have Two Servers!

Right now, you have:
1. ❌ **Django server** running on port 8000 (NOT the bot)
2. ⏸️  **WhatsApp bot** (FastAPI) - NOT running yet

---

## ✅ Quick Start (3 Steps)

### Step 1: Start the WhatsApp Bot

```bash
cd /Users/shachithakur/gyde-ai-whatsapp
./start_bot.sh
```

Or manually:
```bash
cd /Users/shachithakur/gyde-ai-whatsapp
python server.py
```

**Look for this output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ **Bot is now running!**

---

### Step 2: Test It (New Terminal)

Open a new terminal and run:
```bash
curl http://localhost:8000/
```

**Should see:**
```json
{
  "status": "running",
  "service": "WhatsApp Reservation Agent"
}
```

✅ **Bot is responding!**

---

### Step 3: Test AI Response

```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "1234567890",
            "text": {"body": "Check availability for 2 people"},
            "id": "test123"
          }],
          "contacts": [{
            "profile": {"name": "Test User"}
          }]
        }
      }]
    }]
  }'
```

**Check bot terminal, should see:**
```
📱 Message from 1234567890
🤖 Calling AI agent...
✅ AI response generated
```

✅ **Bot is talking!**

---

## 🎯 Full Test with WhatsApp

### 1. Keep bot running (from Step 1)

### 2. Start ngrok (new terminal)
```bash
ngrok http 8000
```

Copy the URL: `https://abc123.ngrok.io`

### 3. Configure WhatsApp webhook
- Go to AiSensy or Meta dashboard
- Set webhook: `https://abc123.ngrok.io/webhook`

### 4. Send WhatsApp message
```
Hi! Check availability for 2 people from 15th December
```

### 5. Watch bot terminal
You should see the AI processing and responding!

✅ **Bot is fully working!**

---

## 🐛 Common Issues

### Issue 1: "Port 8000 already in use"
**Solution:** The Django server is using it. Run:
```bash
./start_bot.sh
```
It will ask if you want to stop the Django server. Say yes.

---

### Issue 2: "ModuleNotFoundError"
**Solution:**
```bash
pip install -r requirements.txt
```

---

### Issue 3: Bot responds but with errors
**Check:** `.env` file has these configured:
- `GOOGLE_API_KEY`
- `TRAVEL_STUDIO_BEARER_TOKEN`
- `AISENSY_PROJECT_ID` and `AISENSY_PROJECT_API_PWD`

---

## ✅ Checklist

Before saying "bot is working":

- [ ] Bot server running (FastAPI, not Django)
- [ ] Can access http://localhost:8000/
- [ ] Sees "WhatsApp Reservation Agent" (not Django page)
- [ ] Webhook test shows "Message queued successfully"
- [ ] Logs show "AI response generated"
- [ ] (Optional) Receives WhatsApp reply

---

## 📁 All Test Files Created

1. **`HOW_TO_TEST_BOT.md`** - Complete testing guide
2. **`START_WHATSAPP_BOT.md`** - How to start the bot
3. **`TESTING_SUMMARY.md`** - This file (quick reference)
4. **`start_bot.sh`** - One-command startup script
5. **`test_bot_quick.sh`** - Quick test script

---

## 🎯 TL;DR

```bash
# Terminal 1 - Start bot
cd /Users/shachithakur/gyde-ai-whatsapp
./start_bot.sh

# Terminal 2 - Test it
curl http://localhost:8000/ | grep "WhatsApp"
```

If you see "WhatsApp Reservation Agent" → **Bot is talking!** ✅

---

**Need detailed help?** Read: `HOW_TO_TEST_BOT.md`
