# Booking API Validation Fix

## Problem
The Travel Studio API was returning validation errors when creating bookings:
```json
{
  "success": false,
  "message": "Validation error",
  "error": "Validation error"
}
```

## Root Cause
The API has two different error response formats:
1. **400 Bad Request** - Generic "Validation error" with no details (happens when optional fields have invalid values)
2. **422 Unprocessable Entity** - Detailed validation errors with field-specific messages

**Key Issue:** The `num_nights` field is **REQUIRED** by the API, even though it can be calculated from check-in/check-out dates.

## Solution
Ensure `num_nights` is always calculated and included in booking requests.

### Required Fields
```python
{
    "guest_name": str,        # Guest full name
    "guest_phone": str,       # Format: +919876543210
    "guest_email": str,       # Valid email
    "room_category": str,     # "Deluxe", "Luxury Cottage", "basic"
    "num_adults": int,        # Number of adults (>= 1)
    "num_children": int,      # Number of children (>= 0)
    "check_in_date": str,     # ISO format: YYYY-MM-DDTHH:MM:SS.SSSZ
    "check_out_date": str,    # ISO format: YYYY-MM-DDTHH:MM:SS.SSSZ
    "num_nights": int         # REQUIRED! (checkout.date() - checkin.date()).days
}
```

### Optional Fields
```python
{
    "booking_channel": str,      # "whatsapp", "direct", etc. (defaults to null)
    "payment_status": str,       # "Unpaid", "Paid" (defaults to "Unpaid")
    "special_requests": str      # Any special requests
}
```

## Code Fix
The fix is already implemented in `services/travel_studio_service.py` (lines 206-210):

```python
# Calculate num_nights if not provided
if num_nights is None:
    checkin = datetime.fromisoformat(check_in_date.replace('Z', '+00:00'))
    checkout = datetime.fromisoformat(check_out_date.replace('Z', '+00:00'))
    # Use date() to get proper day count (15th to 17th = 2 nights)
    num_nights = (checkout.date() - checkin.date()).days
```

## Testing Results
✅ **Successful Bookings Created:**
- `BK1765264657625VO0V4` - Deluxe room, 2 nights
- `BK1765264672995CVP6W` - Luxury Cottage, 3 nights (with all optional fields)

## API Behavior Notes
1. When `num_children: 0` is sent, the API stores it as `null`
2. When `booking_channel` is omitted, it defaults to `null`
3. The API automatically assigns a room from the specified category
4. A `guest_id` is automatically created and linked to the booking
5. Bookings are created with status "Reserved" and payment_status "Unpaid"

## Date Calculation Examples
```python
# Example 1: Dec 15 to Dec 17
check_in = "2025-12-15T14:00:00.000Z"
check_out = "2025-12-17T10:00:00.000Z"
num_nights = (Dec 17 - Dec 15).days = 2 nights ✅

# Example 2: Dec 20 to Dec 22
check_in = "2025-12-20T14:00:00.000Z"
check_out = "2025-12-22T10:00:00.000Z"
num_nights = (Dec 22 - Dec 20).days = 2 nights ✅
```

## What Was Fixed
✅ Date calculation now uses `.date()` for proper day count  
✅ `num_nights` is always calculated and sent to API  
✅ Room type mapping added (COTTAGE → Luxury Cottage, DELUXE → Deluxe)  
✅ Payment link format added to prompts  

## Next Steps
1. Test end-to-end booking flow through WhatsApp
2. Monitor booking creation logs for any edge cases
3. Add email notification endpoint for cancellation/upgrade requests
