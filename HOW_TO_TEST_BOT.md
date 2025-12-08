# 🤖 How to Test If Your WhatsApp Bot Is Talking

## Quick Answer

There are **3 ways** to test your bot:

1. ✅ **Local webhook test** (fastest, no WhatsApp needed)
2. ✅ **ngrok + real WhatsApp** (full end-to-end test)
3. ✅ **Check server status** (verify it's running)

---

## Method 1: Local Webhook Test (Recommended First)

### Step 1: Start the Server

Open Terminal 1:
```bash
cd /Users/shachithakur/gyde-ai-whatsapp
python server.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ If you see this, server is running!

---

### Step 2: Test the Webhook

Open Terminal 2 (keep server running in Terminal 1):
```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "1234567890",
            "text": {"body": "Hello! Tell me about your hotel"},
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

---

### Step 3: Check the Response

**What should happen:**

1. **Terminal 2** (curl) shows:
   ```json
   {"status": "success"}
   ```

2. **Terminal 1** (server logs) shows:
   ```
   📱 Message from 1234567890: Hello! Tell me about your hotel...
   👤 User: Test User
   📤 Queueing to QStash for background processing
   ✅ Message queued successfully!
   ```

3. A few seconds later, you'll see:
   ```
   🔄 /process-async called by QStash
   📱 Processing message from 1234567890
   🤖 Calling AI agent...
   ✅ AI response generated: Welcome to our hotel...
   ```

✅ **If you see all this, your bot is talking!**

---

## Method 2: Test with Real WhatsApp (Full Test)

This tests the complete flow including actual WhatsApp messages.

### Step 1: Start the Server

```bash
cd /Users/shachithakur/gyde-ai-whatsapp
python server.py
```

---

### Step 2: Expose Server with ngrok

Open a **new terminal** (Terminal 2):
```bash
ngrok http 8000
```

**Output:**
```
Forwarding  https://abc123xyz.ngrok.io -> http://localhost:8000
```

✅ Copy the `https://abc123xyz.ngrok.io` URL

---

### Step 3: Configure WhatsApp Webhook

#### For AiSensy:
1. Go to https://app.aisensy.com
2. Navigate to Settings → Webhooks
3. Set webhook URL: `https://abc123xyz.ngrok.io/webhook`
4. Set verify token: (your `WEBHOOK_VERIFY_TOKEN` from `.env`)
5. Save

#### For Meta WhatsApp Business API:
1. Go to https://developers.facebook.com
2. Your App → WhatsApp → Configuration
3. Webhook URL: `https://abc123xyz.ngrok.io/webhook`
4. Verify token: (your `WEBHOOK_VERIFY_TOKEN` from `.env`)
5. Subscribe to messages

---

### Step 4: Send a WhatsApp Message

Send a message to your bot's WhatsApp number:
```
Hi! Do you have rooms available next week?
```

---

### Step 5: Check Server Logs

You should see in Terminal 1:
```
📱 Message from +919876543210: Hi! Do you have rooms available next week?
👤 User: John Doe
📤 Queueing to QStash for background processing
✅ Message queued successfully!
🔄 /process-async called by QStash
🤖 Calling AI agent...
✅ AI response generated: I'd be happy to help...
📤 Sending to WhatsApp via AiSensy...
✅ Message sent successfully to +919876543210
```

---

### Step 6: Check WhatsApp

You should receive a reply from the bot! 🎉

---

## Method 3: Quick Status Check

### Check if server is running:
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

---

### Check configuration:
```bash
curl http://localhost:8000/config-status
```

**Expected:**
```json
{
  "aisensy_configured": true,
  "qstash_configured": true,
  "travel_studio_configured": true,
  ...
}
```

---

### Check health:
```bash
curl http://localhost:8000/health
```

**Expected:**
```json
{
  "status": "healthy",
  "aisensy_configured": true,
  "qstash_configured": true
}
```

---

## 🐛 Troubleshooting

### Problem 1: Server won't start

**Error:** `ModuleNotFoundError: No module named 'twilio'`

**Fix:**
```bash
pip install -r requirements.txt
```

---

### Problem 2: Webhook returns success but no AI response

**Check:**
1. Is QStash configured?
   ```bash
   curl http://localhost:8000/config-status
   ```
   Should show `"qstash_configured": true`

2. Check `.env` file has:
   ```
   QSTASH_TOKEN="eyJ..."
   QSTASH_URL="https://qstash.upstash.io"
   ```

---

### Problem 3: Bot responds but with errors

**Check logs for:**
- `❌ Error` messages
- `Failed to call check_availability`
- `Tool execution failed`

**Common fixes:**
- Verify `TRAVEL_STUDIO_BEARER_TOKEN` is valid (expires Feb 8, 2025)
- Check `GOOGLE_API_KEY` is set
- Ensure database is accessible

---

### Problem 4: No WhatsApp message received

**Check:**
1. **ngrok is running** and URL is correct in webhook settings
2. **Webhook is verified** (green checkmark in AiSensy/Meta dashboard)
3. **Phone number is correct** - Message the right bot number
4. **WhatsApp permissions** - Bot has permission to send messages

---

## 📋 Quick Diagnostic Checklist

Run these commands to verify everything:

```bash
# 1. Check server is running
curl http://localhost:8000/health

# 2. Check configuration
curl http://localhost:8000/config-status

# 3. Test webhook
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"entry":[{"changes":[{"value":{"messages":[{"from":"1234567890","text":{"body":"test"},"id":"test123"}],"contacts":[{"profile":{"name":"Test"}}]}}]}]}'

# 4. Check if bot can check availability
python test_check_availability.py

# 5. Check advanced features
python test_advanced_booking_features.py
```

**All should return success!** ✅

---

## 🎯 Expected Behavior

### When bot is working correctly:

1. **Receives message** → Logs show incoming message
2. **Queues to QStash** → `Message queued successfully`
3. **Processes async** → `/process-async called`
4. **AI generates response** → `AI response generated`
5. **Sends via WhatsApp** → `Message sent successfully`
6. **User receives reply** → Reply arrives in WhatsApp

**Total time:** 3-10 seconds from message to reply

---

## 💡 Test Messages to Try

### General conversation:
```
Hi! Tell me about your hotel
```

### Availability check:
```
Check availability for 2 people from 15th December to 17th December
```

### Booking inquiry:
```
I want to book a Luxury Cottage for 3 nights
```

### Multi-room:
```
I need 3 rooms for a family reunion
```

### Modification:
```
Can I extend my stay by 2 days?
```

---

## 🔍 Logs to Look For

### ✅ Good logs (everything working):
```
📱 Message from +919876543210: Hello...
👤 User: John Doe
📤 Queueing to QStash for background processing
✅ Message queued successfully! QStash MessageID: msg_123
🔄 /process-async called by QStash
🤖 Calling AI agent...
✅ AI response generated: I'd be happy to help...
📤 Sending to WhatsApp via AiSensy...
✅ Message sent successfully to +919876543210
```

### ❌ Problem logs (something wrong):
```
❌ QStash error: 401 Unauthorized
❌ Failed to send message to +919876543210
❌ Error in async processing: ...
❌ Tool execution failed: check_availability
```

---

## 📞 Quick Help Commands

### View server logs in real-time:
```bash
# Run server with verbose logging
python server.py
```

### Test specific features:
```bash
# Test availability checking
python test_check_availability.py

# Test advanced booking features
python test_advanced_booking_features.py
```

### Check environment variables:
```bash
# Check if all required vars are set
cat .env | grep -E "GOOGLE_API_KEY|AISENSY|QSTASH|TRAVEL_STUDIO"
```

---

## ✨ Success Indicators

You'll know the bot is working when:

✅ Server starts without errors  
✅ Health check returns "healthy"  
✅ Config status shows all features configured  
✅ Webhook test returns success  
✅ Logs show "Message queued successfully"  
✅ Logs show "AI response generated"  
✅ Logs show "Message sent successfully"  
✅ You receive a reply in WhatsApp  

---

## 🎉 Quick Start Script

Save this as `test_bot.sh`:
```bash
#!/bin/bash

echo "🤖 Testing WhatsApp Bot..."
echo ""

echo "1️⃣ Checking server health..."
curl -s http://localhost:8000/health | jq .

echo ""
echo "2️⃣ Checking configuration..."
curl -s http://localhost:8000/config-status | jq .

echo ""
echo "3️⃣ Testing webhook..."
curl -s -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"entry":[{"changes":[{"value":{"messages":[{"from":"1234567890","text":{"body":"Hello"},"id":"test123"}],"contacts":[{"profile":{"name":"Test"}}]}}]}]}' | jq .

echo ""
echo "✅ If all responses show success, your bot is working!"
```

Run it:
```bash
chmod +x test_bot.sh
./test_bot.sh
```

---

**Need help?** Check the server logs for detailed error messages!
