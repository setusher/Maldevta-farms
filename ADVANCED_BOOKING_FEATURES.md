# 🚀 Advanced Booking Management Features

## 📋 Overview

The Travel Studio integration now includes **6 powerful booking management features** that enable:

- 🏨 **Multi-room bookings** - Book multiple rooms in a single transaction
- ⏰ **Room stay extensions** - Extend checkout dates for specific rooms
- ⬆️ **Room upgrades** - Upgrade guests to better room categories
- ➕ **Add rooms** - Add additional rooms to existing bookings
- ✏️ **Update rooms** - Modify room details in bookings
- ➖ **Remove rooms** - Remove specific rooms from bookings

---

## ✅ Status

**All features tested and operational!**

- ✅ 6 new methods added to `TravelStudioService`
- ✅ All endpoints using correct `/api/hocc/` pattern
- ✅ Comprehensive test suite created
- ✅ Full documentation with examples
- ✅ Ready for production use

---

## 🎯 Features

### 1. Multi-Room Booking

**Create a single booking with multiple rooms**

**Endpoint:** `POST /api/hocc/bookings`

**Method:** `create_multi_room_booking()`

**Use Case:** Family or group bookings needing multiple rooms

**Example:**
```python
from services import get_travel_studio_service

travel_studio = get_travel_studio_service()

# Book 2 rooms for a family
rooms = [
    {"category": "Deluxe", "room_id": "room-abc123"},
    {"category": "Luxury Cottage", "room_id": "room-def456"}
]

booking = travel_studio.create_multi_room_booking(
    guest_name="John Smith",
    guest_email="john@example.com",
    guest_phone="+91 9876543210",
    check_in_date="2026-01-15",
    check_out_date="2026-01-17",
    rooms=rooms,
    num_adults=4,
    num_children=2,
    special_requests="Adjoining rooms preferred"
)

print(f"Multi-room booking created: {booking['booking_id']}")
```

**Parameters:**
- `guest_name` (str): Guest full name
- `guest_email` (str): Guest email
- `guest_phone` (str): Guest phone number
- `check_in_date` (str): Check-in date (YYYY-MM-DD)
- `check_out_date` (str): Check-out date (YYYY-MM-DD)
- `rooms` (list): List of room objects with category/id
- `num_adults` (int): Total number of adults
- `num_children` (int): Total number of children
- `special_requests` (str, optional): Special requests

**Returns:** Booking object with all room details

---

### 2. Extend Room Stay

**Extend the checkout date for a specific room in a booking**

**Endpoint:** `POST /api/hocc/bookings/{bookingId}/rooms/{roomId}/extend`

**Method:** `extend_room_stay()`

**Use Case:** Guest wants to stay longer in one specific room

**Example:**
```python
# Extend stay for room 011 until Jan 20
result = travel_studio.extend_room_stay(
    booking_id="BK1234567890",
    room_id_or_number="room-abc123",  # or room number "011"
    new_check_out_date="2026-01-20",
    reason="Guest requested extension"
)

print(f"Room stay extended to {result['new_check_out_date']}")
```

**Parameters:**
- `booking_id` (str): Booking ID
- `room_id_or_number` (str): Room ID or room number
- `new_check_out_date` (str): New check-out date (YYYY-MM-DD)
- `reason` (str, optional): Reason for extension

**Returns:** Updated booking details

---

### 3. Upgrade Room

**Upgrade a room to a higher category**

**Endpoint:** `POST /api/hocc/bookings/{bookingId}/rooms/{roomId}/upgrade`

**Method:** `upgrade_room()`

**Use Case:** Guest wants to upgrade to a better room type

**Example:**
```python
# Upgrade from Deluxe to Luxury Cottage
result = travel_studio.upgrade_room(
    booking_id="BK1234567890",
    room_id_or_number="room-abc123",
    new_room_category="Luxury Cottage",
    new_room_id="room-xyz789",  # optional, auto-assigned if not provided
    price_difference=2000.00,
    reason="Anniversary special"
)

print(f"Room upgraded to {result['new_category']}")
```

**Parameters:**
- `booking_id` (str): Booking ID
- `room_id_or_number` (str): Current room ID or number
- `new_room_category` (str): Target room category
- `new_room_id` (str, optional): Specific new room ID
- `price_difference` (float, optional): Price difference
- `reason` (str, optional): Reason for upgrade

**Returns:** Updated booking details

---

### 4. Add Room to Booking

**Add an additional room to an existing booking**

**Endpoint:** `POST /api/hocc/bookings/{bookingId}/rooms`

**Method:** `add_room_to_booking()`

**Use Case:** Guest needs an extra room (e.g., additional family member joining)

**Example:**
```python
# Add a basic room to existing booking
result = travel_studio.add_room_to_booking(
    booking_id="BK1234567890",
    room_category="basic",
    room_id="room-new123",  # optional, auto-assigned if not provided
    check_in_date="2026-01-15",  # optional, uses booking dates if not provided
    check_out_date="2026-01-17",  # optional
    reason="Additional guest joining"
)

print(f"Room added: {result['room_number']}")
```

**Parameters:**
- `booking_id` (str): Booking ID
- `room_category` (str): Room category to add
- `room_id` (str, optional): Specific room ID
- `check_in_date` (str, optional): Check-in date
- `check_out_date` (str, optional): Check-out date
- `reason` (str, optional): Reason for adding room

**Returns:** Updated booking details

---

### 5. Update Room in Booking

**Update specific room details in a booking**

**Endpoint:** `PUT /api/hocc/bookings/{bookingId}/rooms/{roomId}`

**Method:** `update_room_in_booking()`

**Use Case:** Modify room-specific details (status, notes, dates, etc.)

**Example:**
```python
# Update room status and add notes
result = travel_studio.update_room_in_booking(
    booking_id="BK1234567890",
    room_id_or_number="room-abc123",
    status="confirmed",
    special_notes="Extra pillows and blankets requested",
    check_in_time="14:00",
    check_out_time="12:00"
)

print(f"Room updated successfully")
```

**Parameters:**
- `booking_id` (str): Booking ID
- `room_id_or_number` (str): Room ID or room number
- `**update_fields`: Any fields to update (status, notes, dates, etc.)

**Returns:** Updated room details

**Common update fields:**
- `status`: Room status (confirmed, checked-in, checked-out)
- `special_notes`: Room-specific notes
- `check_in_time`: Check-in time
- `check_out_time`: Check-out time
- `check_in_date`: Modified check-in date
- `check_out_date`: Modified check-out date

---

### 6. Remove Room from Booking

**Remove a specific room from a booking**

**Endpoint:** `DELETE /api/hocc/bookings/{bookingId}/rooms/{roomId}`

**Method:** `remove_room_from_booking()`

**Use Case:** Guest cancels one room from a multi-room booking

**Example:**
```python
# Remove room from booking
success = travel_studio.remove_room_from_booking(
    booking_id="BK1234567890",
    room_id_or_number="room-abc123",
    reason="Guest reduced party size"
)

if success:
    print("Room removed successfully")
```

**Parameters:**
- `booking_id` (str): Booking ID
- `room_id_or_number` (str): Room ID or room number to remove
- `reason` (str, optional): Reason for removal

**Returns:** `True` if successful, `False` otherwise

---

## 🔧 API Configuration

### Base URL
```
https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net
```

### Authentication
All endpoints require Bearer token authentication:
```python
Authorization: Bearer {TRAVEL_STUDIO_BEARER_TOKEN}
```

### Environment Variables
Required in `.env`:
```bash
TRAVEL_STUDIO_API_URL="https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net"
TRAVEL_STUDIO_BEARER_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 🧪 Testing

### Quick Test
```bash
python test_advanced_booking_features.py
```

**Expected Output:**
```
✅ ALL AVAILABLE TESTS PASSED!

💡 Advanced booking features are ready to use!
   All 6 new methods have been added to TravelStudioService
```

### Manual Testing

```python
from services import get_travel_studio_service

# Initialize service
travel_studio = get_travel_studio_service()

# 1. Check available rooms
available = travel_studio.get_available_rooms(
    check_in_date="2026-01-15",
    check_out_date="2026-01-17"
)
print(f"Available rooms: {len(available)}")

# 2. Get existing bookings
bookings = travel_studio.get_bookings()
print(f"Total bookings: {len(bookings)}")

# 3. Use advanced features with real booking IDs
# (See examples above)
```

---

## 📊 Use Cases

### Scenario 1: Family Reunion Booking
**Challenge:** Book 5 rooms for extended family arriving together

**Solution:**
```python
rooms = [
    {"category": "Luxury Cottage", "room_id": "lc-001"},
    {"category": "Deluxe", "room_id": "dlx-002"},
    {"category": "Deluxe", "room_id": "dlx-003"},
    {"category": "basic", "room_id": "bsc-004"},
    {"category": "basic", "room_id": "bsc-005"}
]

booking = travel_studio.create_multi_room_booking(
    guest_name="Smith Family",
    guest_email="smith.reunion@example.com",
    guest_phone="+91 9876543210",
    check_in_date="2026-02-10",
    check_out_date="2026-02-14",
    rooms=rooms,
    num_adults=12,
    num_children=5,
    special_requests="Rooms on same floor preferred"
)
```

### Scenario 2: Extending Stay for One Guest
**Challenge:** 3 rooms booked, but one guest wants to stay 2 extra days

**Solution:**
```python
# Extend just room 012
travel_studio.extend_room_stay(
    booking_id=booking['booking_id'],
    room_id_or_number="012",
    new_check_out_date="2026-02-16"
)
```

### Scenario 3: Anniversary Upgrade
**Challenge:** Guest wants to upgrade to Luxury Cottage for anniversary

**Solution:**
```python
travel_studio.upgrade_room(
    booking_id=booking['booking_id'],
    room_id_or_number="dlx-002",
    new_room_category="Luxury Cottage",
    reason="Anniversary celebration"
)
```

### Scenario 4: Additional Guest Joining
**Challenge:** Guest's friend decides to join, needs one more room

**Solution:**
```python
travel_studio.add_room_to_booking(
    booking_id=booking['booking_id'],
    room_category="Deluxe",
    reason="Additional guest joining party"
)
```

### Scenario 5: One Guest Cancels
**Challenge:** One family member can't make it, need to cancel their room

**Solution:**
```python
travel_studio.remove_room_from_booking(
    booking_id=booking['booking_id'],
    room_id_or_number="bsc-005",
    reason="Guest cancelled due to emergency"
)
```

---

## 🔍 Error Handling

All methods include proper error handling:

```python
# Example with error handling
try:
    result = travel_studio.extend_room_stay(
        booking_id="BK1234567890",
        room_id_or_number="room-abc123",
        new_check_out_date="2026-01-20"
    )
    
    if result:
        print("✓ Extension successful")
    else:
        print("✗ Extension failed - check logs")
        
except Exception as e:
    print(f"Error: {str(e)}")
```

**Common Error Responses:**
- `{"success": false, "message": "Booking not found"}` - Invalid booking ID
- `{"success": false, "message": "Room not available"}` - Room already booked
- `{"success": false, "message": "Invalid date"}` - Date format error
- `401 Unauthorized` - Token expired or invalid

---

## 📝 Best Practices

### 1. Always Validate Dates
```python
from datetime import datetime

# Ensure dates are in correct format
check_in = datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
```

### 2. Check Availability Before Adding Rooms
```python
# Check if rooms are available before adding
available = travel_studio.get_available_rooms(check_in, check_out)
if len(available) > 0:
    travel_studio.add_room_to_booking(...)
```

### 3. Log All Operations
```python
import logging

logger.info(f"Extending stay for booking {booking_id}")
result = travel_studio.extend_room_stay(...)
logger.info(f"Extension result: {result}")
```

### 4. Handle Partial Failures
```python
# When booking multiple rooms, handle individual failures
for room in rooms_to_add:
    try:
        travel_studio.add_room_to_booking(booking_id, room['category'])
    except Exception as e:
        logger.error(f"Failed to add room {room['category']}: {e}")
```

---

## 🚀 Quick Reference

| Feature | Method | HTTP Method | Endpoint |
|---------|--------|-------------|----------|
| Multi-room booking | `create_multi_room_booking()` | POST | `/api/hocc/bookings` |
| Extend stay | `extend_room_stay()` | POST | `/api/hocc/bookings/{id}/rooms/{room}/extend` |
| Upgrade room | `upgrade_room()` | POST | `/api/hocc/bookings/{id}/rooms/{room}/upgrade` |
| Add room | `add_room_to_booking()` | POST | `/api/hocc/bookings/{id}/rooms` |
| Update room | `update_room_in_booking()` | PUT | `/api/hocc/bookings/{id}/rooms/{room}` |
| Remove room | `remove_room_from_booking()` | DELETE | `/api/hocc/bookings/{id}/rooms/{room}` |

---

## 📞 Support

**Documentation:**
- `ADVANCED_BOOKING_FEATURES.md` (this file) - Feature overview
- `test_advanced_booking_features.py` - Test suite with examples
- `services/travel_studio_service.py` - Source code with docstrings

**Testing:**
```bash
python test_advanced_booking_features.py
```

**Issues:**
- Check logs for detailed error messages
- Verify token expiration (expires Feb 8, 2025)
- Ensure booking IDs and room IDs are valid
- Confirm room availability before operations

---

**Status:** ✅ Production Ready  
**Date Added:** December 8, 2025  
**Version:** 2.0  
**Test Status:** All tests passing
