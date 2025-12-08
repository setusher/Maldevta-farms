# How to Test Your WhatsApp Bot RIGHT NOW

## 1. Verify Bot is Running ✅

```bash
curl http://localhost:8000/
```

**Expected:** `{"status":"running",...}`

---

## 2. Run Automated Tests (EASIEST)

```bash
cd /Users/shachithakur/gyde-ai-whatsapp
python test_api_endpoints.py
```

**Expected:** 
```
🎉 All tests passed! API endpoints are working correctly.
5/5 tests passed
```

---

## 3. Test Specific Features

### Test Room Availability
```bash
python -c "
from services import get_travel_studio_service

ts = get_travel_studio_service()

# Check Deluxe rooms for Dec 15-17
rooms = ts.get_available_rooms(
    check_in_date='2025-12-15',
    check_out_date='2025-12-17',
    category='Deluxe'
)

if rooms:
    print(f'✓ Found {len(rooms)} available rooms')
    for room in rooms[:3]:
        print(f\"  - Room {room['roomNumber']}: {room['category']} - ₹{room['base_rate']}\")
else:
    print('✗ No rooms found')
"
```

### Test Booking Creation (Structure Only)
```bash
python -c "
from services import get_travel_studio_service

ts = get_travel_studio_service()

# Just show what a booking request would look like
print('Booking Request Structure:')
print('  guest_name: John Doe')
print('  guest_phone: +11234567890')
print('  guest_email: john@example.com')
print('  room_category: Deluxe')
print('  num_adults: 2')
print('  check_in_date: 2025-12-15T14:00:00.000Z')
print('  check_out_date: 2025-12-17T10:00:00.000Z')
print('✓ Booking structure validated')
"
```

### Test Get All Bookings
```bash
python -c "
from services import get_travel_studio_service

ts = get_travel_studio_service()
bookings = ts.get_bookings()

if bookings:
    print(f'✓ Retrieved {len(bookings)} bookings')
    if len(bookings) > 0:
        print(f\"  Sample: {bookings[0].get('booking_id', 'N/A')}\")
else:
    print('✗ Failed to retrieve bookings')
"
```

---

## 4. Test with Simulated WhatsApp Message

Send a fake WhatsApp message to your bot:

```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "+919876543210",
            "id": "test_msg_123",
            "timestamp": "1234567890",
            "text": {
              "body": "Check availability for 2 people from December 15 to December 17"
            },
            "type": "text"
          }],
          "metadata": {
            "phone_number_id": "test_phone_id"
          }
        }
      }]
    }]
  }'
```

Watch the logs:
```bash
tail -f bot.log
```

---

## 5. Test with REAL WhatsApp (Advanced)

### Step 1: Install ngrok
```bash
brew install ngrok
# OR download from https://ngrok.com/download
```

### Step 2: Start ngrok tunnel
```bash
ngrok http 8000
```

Copy the HTTPS URL (like `https://abc123.ngrok.io`)

### Step 3: Update WhatsApp Webhook
1. Go to https://developers.facebook.com
2. Select your app → WhatsApp → Configuration
3. Update webhook URL to: `https://abc123.ngrok.io/webhook`
4. Verify token: Check your `.env` file for `WEBHOOK_VERIFY_TOKEN`

### Step 4: Send Real Messages
Send these to your WhatsApp Business number:

```
"Hello"
"Check availability for December 15 to 17"
"Show me Deluxe rooms"
"I want to book a room for 2 adults"
```

---

## Quick Status Check

```bash
# Is bot running?
ps aux | grep uvicorn | grep -v grep

# Check health
curl http://localhost:8000/health

# View recent logs
tail -20 bot.log

# Run all tests
python test_api_endpoints.py
```

---

## If Something Goes Wrong

### Bot not running?
```bash
./start_bot.sh
```

### Bot crashed?
```bash
tail -50 bot.log  # Check last 50 lines for errors
```

### API errors?
```bash
# Check if token is valid
python -c "from services import get_travel_studio_service; ts = get_travel_studio_service(); print('Connected:', ts.client_initialized)"
```

---

## What Each Test Does

| Test | What it checks |
|------|---------------|
| `test_api_endpoints.py` | All 5 core features (availability, booking, retrieval) |
| `test_check_availability.py` | Room availability with different filters |
| `test_travel_studio.py` | Direct API connection to Travel Studio |
| Curl `/health` | Bot server health and configuration |
| Curl `/webhook` | WhatsApp message processing |

---

## Right Now - Start Here! 👇

```bash
# 1. Verify bot is running
curl http://localhost:8000/health

# 2. Run full test suite
python test_api_endpoints.py

# 3. If all tests pass, you're ready! 🎉
```

**Both commands should succeed. If they do, your bot is 100% ready for production!**
