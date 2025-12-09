# Duplicate Booking Prevention Fix

## Problem Encountered

When a user (Shradha, +919334391959) tried to create a booking for Dec 21-25, 2025, the API returned:
```
{"success": false, "message": "Validation error", "error": "Validation error"}
```

## Root Cause

The user already had an existing booking for the same dates:
- **Booking ID**: `BK1765263578215JYU7F`
- **Dates**: Dec 21-25, 2025
- **Room**: Luxury Cottage

The Travel Studio API was correctly rejecting the duplicate booking to prevent double-booking the same guest for overlapping dates. However, the generic "Validation error" message didn't clearly communicate this to the AI agent or user.

## Solution Implemented

Added duplicate booking detection in `services/tool_service.py` (lines 253-272):

### How It Works

1. **Before creating a booking**, the system now:
   - Fetches all existing bookings from the API
   - Normalizes phone numbers for comparison (removes +, spaces, dashes)
   - Checks if the guest has any bookings with overlapping dates

2. **If an overlapping booking is found**:
   - Returns the existing booking instead of creating a new one
   - Provides a helpful message with the existing booking ID
   - Includes the payment link for the existing booking

3. **If no overlap is found**:
   - Proceeds to create the new booking normally

### Code Changes

```python
# Check if guest already has a booking for these dates
phone_number = params.get("phone_number", "")
if phone_number:
    existing_bookings = self.travel_studio.get_bookings()
    if existing_bookings:
        # Normalize phone for comparison
        phone_normalized = phone_number.replace("+", "").replace(" ", "").replace("-", "")
        
        for existing in existing_bookings:
            guest = existing.get("Guest") or {}
            existing_phone = (guest.get("phone") or "").replace("+", "").replace(" ", "").replace("-", "")
            
            if existing_phone == phone_normalized:
                # Check date overlap
                existing_checkin = existing.get("check_in_date", "")[:10]
                existing_checkout = existing.get("check_out_date", "")[:10]
                new_checkin = check_in
                new_checkout = check_out
                
                # Check if dates overlap
                if (existing_checkin <= new_checkout and existing_checkout >= new_checkin):
                    # Found overlapping booking
                    booking_id = existing.get("booking_id")
                    logger.info(f"Guest already has booking {booking_id} for overlapping dates")
                    
                    return {
                        "success": True,
                        "data": existing,
                        "message": f"You already have an existing booking (ID: {booking_id}) for these dates. Payment link: https://maldevtafarms.com/book?bookingId={booking_id}"
                    }
```

## Additional Fix: Float to Integer Conversion

Also fixed numeric fields being sent as floats (2.0) instead of integers (2):

```python
# Ensure numeric fields are integers (AI often sends floats)
num_adults = int(params.get("num_of_adults", 1))
num_children = int(params.get("num_of_children", 0))
```

## Test Results

### Test 1: Existing Booking Detection ✅
```
Input: Shradha (+919334391959) booking Dec 21-25
Output: "You already have an existing booking (ID: BK1765263578215JYU7F) 
         for these dates. Payment link: https://maldevtafarms.com/book?bookingId=BK1765263578215JYU7F"
```

### Test 2: New Booking Creation ✅
```
Input: New user booking Dec 28-30
Output: "New booking created: BK17652685244459Z2CF
         Payment: https://maldevtafarms.com/book?bookingId=BK17652685244459Z2CF"
```

## Benefits

1. **Prevents Double Bookings**: No duplicate reservations for the same guest
2. **Better User Experience**: User gets their existing booking link immediately
3. **API Protection**: Reduces unnecessary API calls and validation errors
4. **Clear Communication**: AI agent can inform users about existing bookings
5. **Data Integrity**: Maintains clean booking records

## Edge Cases Handled

1. **Phone Number Formats**: 
   - `+919334391959`
   - `919334391959`
   - `+91 933 439 1959`
   - All normalized for comparison

2. **Date Overlaps**:
   - Exact match (same dates)
   - Partial overlap (check-in during existing stay)
   - Complete overlap (new dates encompass existing dates)
   - Inverse overlap (existing dates encompass new dates)

3. **Multiple Bookings**:
   - User can have non-overlapping bookings
   - Only prevents overlapping dates for the same guest

## AI Agent Behavior

When a user requests a booking:

**Scenario 1: No Existing Booking**
```
User: "I want to book a cottage for Dec 21-25"
Agent: "Great! Let me create that booking for you..."
Agent: ✅ "Booking confirmed! ID: BK123... Payment link: https://..."
```

**Scenario 2: Existing Booking Found**
```
User: "Send me the booking link"
Agent: "Let me check your booking..."
Agent: ✅ "You already have a booking (ID: BK1765263578215JYU7F) for 
       Dec 21-25. Here's your payment link: https://maldevtafarms.com/book?bookingId=BK1765263578215JYU7F"
```

## Files Modified

- `services/tool_service.py` (lines 253-272)
- `services/travel_studio_service.py` (added logging, integer conversion)

## Performance Impact

- **Minimal**: One additional GET /bookings call before creating a booking
- **Cached**: Could be optimized with session-level caching if needed
- **Trade-off**: Small overhead for better UX and data integrity

## Future Enhancements

1. **Cache Recent Bookings**: Reduce API calls by caching bookings per session
2. **Allow Modifications**: Detect if user wants to modify existing booking
3. **Multiple Rooms**: Allow booking additional rooms for same dates
4. **Booking Status Check**: Only prevent overlap for active bookings (not cancelled)

---

**Status**: ✅ Deployed and Working  
**Date**: December 9, 2024  
**Impact**: Resolved validation errors and improved user experience
