# 🚀 How to Start Your WhatsApp Bot

## Current Situation

You have a **Django server** running on port 8000. This is **NOT** your WhatsApp bot.

Your WhatsApp bot (FastAPI server) needs to be started separately.

---

## ✅ Step-by-Step Instructions

### Step 1: Stop the Django Server (Optional)

If you want to use port 8000 for the WhatsApp bot:

```bash
# Find the process
ps aux | grep "manage.py runserver"

# Kill it (replace PID with actual number)
kill 85815
```

Or just use a different port for the WhatsApp bot (see Step 2).

---

### Step 2: Start the WhatsApp Bot

Open a new terminal and run:

```bash
cd /Users/shachithakur/gyde-ai-whatsapp
python server.py
```

**Expected output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Starting WhatsApp Agent Server (AiSensy + QStash Mode)...
INFO:     Database initialized
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

✅ **If you see this, your WhatsApp bot is now running!**

---

### Step 3: Test the Bot

#### Option A: Quick Test (Terminal)

Open a **new terminal** (keep bot running in the first one):

```bash
curl http://localhost:8000/
```

**Expected:**
```json
{
  "status": "running",
  "service": "WhatsApp Reservation Agent",
  "provider": "AiSensy + WhatsApp Business API",
  "mode": "qstash-async",
  "version": "3.0.0"
}
```

✅ If you see this, bot is working!

---

#### Option B: Test Webhook

```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "1234567890",
            "text": {"body": "Hello! Check availability for 2 people"},
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

**Check the bot terminal**, you should see:
```
📱 Message from 1234567890: Hello! Check availability...
👤 User: Test User
📤 Queueing to QStash for background processing
✅ Message queued successfully!
```

---

### Step 4: Test with Real WhatsApp

#### A. Start ngrok

In a **new terminal**:
```bash
ngrok http 8000
```

**Copy the ngrok URL** (e.g., `https://abc123.ngrok.io`)

#### B. Configure Webhook

Go to your WhatsApp Business API dashboard (AiSensy or Meta):
- Webhook URL: `https://abc123.ngrok.io/webhook`
- Verify token: (from your `.env` file: `WEBHOOK_VERIFY_TOKEN`)

#### C. Send a Message

Send a WhatsApp message to your bot number:
```
Hi! Do you have rooms available next week?
```

#### D. Check Logs

In the bot terminal, you should see:
```
📱 Message from +919876543210: Hi! Do you have rooms...
🤖 Calling AI agent...
✅ AI response generated: I'd be happy to help...
📤 Sending to WhatsApp via AiSensy...
✅ Message sent successfully
```

---

## 🐛 Troubleshooting

### Problem: Port 8000 is already in use

**Error:** `Address already in use`

**Solution:** Use a different port:
```bash
# Edit server.py and change the port at the bottom:
uvicorn.run(app, host="0.0.0.0", port=8001)

# Or stop the Django server first
```

---

### Problem: ModuleNotFoundError

**Error:** `No module named 'fastapi'` or similar

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

---

### Problem: Database connection error

**Error:** `could not connect to server: Connection refused`

**Solution:** Check your `.env` file has correct `DATABASE_URL`

---

### Problem: Bot doesn't respond

**Check:**
1. Is QStash configured? (Check `.env` for `QSTASH_TOKEN`)
2. Is Google API key set? (Check `.env` for `GOOGLE_API_KEY`)
3. Is Travel Studio token set? (Check `.env` for `TRAVEL_STUDIO_BEARER_TOKEN`)

---

## 📋 Quick Checklist

Before testing, ensure:

- [  ] Django server stopped (or using different port)
- [  ] WhatsApp bot running (`python server.py`)
- [  ] See "Uvicorn running" message
- [  ] Can access `http://localhost:8000/`
- [  ] Environment variables configured in `.env`

---

## 🎯 What Each Server Does

### Django Server (Port 8000 currently)
- **What it does:** Some other project (blog?)
- **How to identify:** Shows Django error pages
- **Command:** `python manage.py runserver`

### WhatsApp Bot (FastAPI - should be on port 8000)
- **What it does:** Your WhatsApp booking agent
- **How to identify:** Returns JSON with "WhatsApp Reservation Agent"
- **Command:** `python server.py`

---

## ✨ Quick Start Command

All in one command:
```bash
cd /Users/shachithakur/gyde-ai-whatsapp && python server.py
```

That's it! Your bot should now be running.

---

## 🔍 Verify Bot is Running

Run this in another terminal:
```bash
curl http://localhost:8000/ | grep "WhatsApp"
```

If you see "WhatsApp Reservation Agent", bot is running! ✅

If you see HTML or Django, wrong server is running! ❌

---

## 📞 Need Help?

Check the bot logs - they tell you everything:
- ✅ Green checkmarks = working
- ❌ Red X marks = errors
- 📱 Message received
- 🤖 AI processing
- 📤 Sending response
