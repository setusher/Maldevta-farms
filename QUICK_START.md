# Quick Start Guide - Travel Studio Integration

## ✅ What's Already Done

Your WhatsApp booking system now has a complete Travel Studio API integration ready to use.

## 🔧 Setup (Already Configured)

Environment variables in `.env`:
```bash
TRAVEL_STUDIO_API_URL="https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net"
TRAVEL_STUDIO_BEARER_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## ⚠️ Current Issue

The API endpoints return "404 Route not found". You need the correct endpoint paths from the Travel Studio API documentation.

## 🚀 Once You Have the API Docs

### Step 1: Update Endpoints

Edit `services/travel_studio_service.py` and update the endpoint paths:

```python
# Find methods like this:
def get_bookings(self, ...):
    result = self._make_request("GET", "/api/hotel/bookings", ...)
    
# Change to the correct endpoint:
def get_bookings(self, ...):
    result = self._make_request("GET", "/correct/path", ...)
```

### Step 2: Test the Connection

```bash
python test_travel_api.py
```

### Step 3: Run Full Tests

```bash
python test_travel_studio.py
```

### Step 4: Start Using It

```python
from services import get_travel_studio_service

# Get service instance
travel_studio = get_travel_studio_service()

# Check availability
rooms = travel_studio.get_available_rooms(
    check_in_date="2025-12-15",
    check_out_date="2025-12-17"
)

# Create booking
booking = travel_studio.create_booking(
    guest_name="John Doe",
    guest_email="john@example.com",
    guest_phone="9999999999",
    check_in_date="2025-12-15",
    check_out_date="2025-12-17",
    room_type="Deluxe",
    number_of_guests=2
)
```

## 📚 Documentation Files

- **INTEGRATION_SUMMARY.md** - Complete overview and next steps
- **TRAVEL_STUDIO_INTEGRATION.md** - Detailed usage examples
- **QUICK_START.md** - This file

## 🎯 What You Need

1. Travel Studio API documentation with correct endpoint paths
2. Example API requests/responses
3. Any additional authentication requirements

## 💡 Key Features Available

Once endpoints are correct, you'll have:

- ✅ Booking management (create, read, update, cancel)
- ✅ Room availability checking
- ✅ Guest management
- ✅ Analytics and reports
- ✅ Hotel profile management
- ✅ RESTful API endpoints in your server
- ✅ Complete error handling

## 🔗 Server Endpoints (When Working)

```bash
GET  /travel-studio/bookings
GET  /travel-studio/bookings/{id}
POST /travel-studio/bookings
GET  /travel-studio/rooms/available
GET  /travel-studio/rooms/types
GET  /travel-studio/profile
```

## 📞 Need Help?

Refer to the detailed documentation:
- API usage: `TRAVEL_STUDIO_INTEGRATION.md`
- Integration status: `INTEGRATION_SUMMARY.md`
- Code: `services/travel_studio_service.py`
