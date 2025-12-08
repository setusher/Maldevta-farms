# 🚀 Quick Test Guide - check_availability

## ✅ What's Fixed

The `check_availability` function now works with the Travel Studio API!

- ❌ **Old**: Called broken Vercel endpoint → Always failed
- ✅ **New**: Uses Travel Studio API → Works perfectly!

---

## 🧪 Test 1: Verify Availability Check (30 seconds)

```bash
python test_check_availability.py
```

**Expected Output:**
```
✓ SUCCESS!
  Total available: 7 rooms
  Room categories:
    - basic: 5 rooms @ ₹3500.0/night
    - Luxury Cottage: 2 rooms @ ₹7350.0/night
```

---

## 🤖 Test 2: Test WhatsApp Bot Locally

### Step 1: Start the Server
```bash
python server.py
```

### Step 2: Test with Webhook (in another terminal)
```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "1234567890",
            "text": {"body": "Check availability for 2 people from 15th December to 17th December"},
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

**What Should Happen:**
1. Webhook receives message immediately (returns 200)
2. Message queued to QStash for processing
3. Agent processes request and calls `check_availability`
4. Bot responds with available rooms via WhatsApp

---

## 📱 Test 3: Test with Real WhatsApp (with ngrok)

### Step 1: Start Server
```bash
python server.py
```

### Step 2: Start ngrok (in another terminal)
```bash
ngrok http 8000
```

### Step 3: Configure Webhook
1. Copy the ngrok URL (e.g., `https://abc123.ngrok.io`)
2. Go to your WhatsApp Business API dashboard (AiSensy/Meta)
3. Set webhook to: `https://abc123.ngrok.io/webhook`

### Step 4: Send WhatsApp Message
Send to your bot number:
```
Hi! Check availability for 2 adults from 20th December to 22nd December
```

**Expected Response:**
```
Great! I found several available rooms for your dates:

📅 December 20-22, 2025 (2 nights)
👥 2 adults

Available Rooms:
🏠 Basic Rooms: 5 available
   Rate: ₹3,500/night

🌟 Luxury Cottage: 2 available
   Rate: ₹7,350/night

Would you like to proceed with booking?
```

---

## 🔍 Troubleshooting

### If Test 1 Fails
```bash
# Check if Travel Studio API is accessible
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/health
```

### If WhatsApp Bot Doesn't Respond
1. Check server logs for errors
2. Verify QStash is configured (check `.env`)
3. Test the `/process-async` endpoint directly

### Check Configuration
```bash
curl http://localhost:8000/config-status
```

Should show:
```json
{
  "travel_studio_configured": true,
  "qstash_configured": true,
  ...
}
```

---

## 📊 What Works Now

✅ **Basic availability check**
✅ **Date format conversion** (DD/MM/YYYY)
✅ **Room type filtering** (Deluxe, Luxury Cottage, basic)
✅ **Budget filtering** (max price per night)
✅ **Real-time booking data** from Travel Studio
✅ **Multiple room categories**
✅ **Occupancy-based filtering**

---

## 🎯 Sample Test Messages

Try these with your WhatsApp bot:

1. **Basic availability**:
   - "Check availability for 2 people from 15/12/2025 to 17/12/2025"
   - "Do you have rooms available next week for 2 adults?"

2. **With room type**:
   - "Show me Luxury Cottage availability for Christmas week"
   - "I need a basic room for 2 nights starting tomorrow"

3. **With budget**:
   - "What rooms do you have under 5000 rupees per night?"
   - "Show affordable rooms for December 20-22"

---

## 🚨 Important Notes

1. **Date Format**: Bot expects DD/MM/YYYY or natural language
2. **API Token**: Expires Feb 8, 2025 - update in `.env` if needed
3. **Room Categories**: basic, Deluxe, Luxury Cottage (case-sensitive in API)
4. **Booking Times**: Check-in 8:30 AM, Check-out 6:30 AM (IST)

---

## ✨ Success Indicators

You'll know it's working when:

✅ Test script shows "ALL TESTS PASSED"
✅ Server starts without errors
✅ Webhook returns 200 status
✅ Bot responds with room availability
✅ Response includes accurate room counts and prices
✅ No 404 or API errors in logs

---

**Need Help?** Check `AVAILABILITY_CHECK_FIXED.md` for detailed technical info.
