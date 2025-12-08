# 🔍 Singhana Haveli vs Maldevta Farms - Endpoint Analysis

## 📊 Current Endpoint Comparison

### ✅ Currently Implemented for Singhana (via old Vercel API)

| Endpoint | Purpose | Status | Maldevta Needs This? |
|----------|---------|--------|---------------------|
| `check_availability` | Check room availability | ✅ NOW USES TRAVEL STUDIO | ✅ YES - Working |
| `create_booking_reservation` | Create room booking | ⚠️ USES VERCEL | ✅ YES - Needs Travel Studio |
| `create_day_outing_reservation` | Book day outing | ⚠️ USES VERCEL | ❓ MAYBE - Check if needed |
| `create_event_inquiry` | Create event inquiry | ⚠️ USES VERCEL | ✅ YES - Needs Travel Studio |
| `lead_gen` | Generate lead | ⚠️ USES VERCEL | ✅ YES - For follow-ups |
| `human_followup` | Schedule callback | ⚠️ USES VERCEL | ✅ YES - For complex requests |
| `confirm_payment_details` | Check payment status | ⚠️ USES VERCEL | ✅ YES - Payment verification |
| `general_info` | Get hotel info | ⚠️ USES VERCEL | ❓ CAN BE HARDCODED |
| `get_all_room_reservations` | List bookings (admin) | ⚠️ USES VERCEL | ✅ YES - Use Travel Studio |
| `get_all_day_outing_reservations` | List day outings | ⚠️ USES VERCEL | ❓ MAYBE |
| `get_all_event_inquiries` | List event inquiries | ⚠️ USES VERCEL | ✅ YES - Use Travel Studio |
| `check_hourly_availability` | Check hourly slots | ⚠️ USES VERCEL | ❌ NO - Maldevta doesn't offer |
| `create_hourly_booking_reservation` | Book hourly | ⚠️ USES VERCEL | ❌ NO - Maldevta doesn't offer |
| `get_hourly_booking_by_id` | Get hourly booking | ⚠️ USES VERCEL | ❌ NO - Maldevta doesn't offer |
| `location_info` | Send location | ⚠️ USES VERCEL | ✅ YES - Send via WhatsApp |
| `request_update_or_cancel` | Cancel/update booking | ✅ WORKING (email) | ✅ YES - Already working |

---

## 🎯 What Maldevta DEFINITELY Needs

### 1. **Room Booking** (HIGH PRIORITY)
- ✅ `check_availability` - **DONE** (Using Travel Studio)
- ⚠️ `create_booking_reservation` - **NEEDS TRAVEL STUDIO INTEGRATION**
- ✅ `get_all_room_reservations` - Use Travel Studio's `get_bookings()`

### 2. **Event Management** (HIGH PRIORITY)
- ⚠️ `create_event_inquiry` - **NEEDS TRAVEL STUDIO OR EMAIL**
- ⚠️ `get_all_event_inquiries` - **NEEDS TRAVEL STUDIO**

### 3. **Lead & Follow-up** (MEDIUM PRIORITY)
- ⚠️ `lead_gen` - **NEEDS DATABASE OR EMAIL**
- ⚠️ `human_followup` - **NEEDS DATABASE OR EMAIL**

### 4. **Payment** (MEDIUM PRIORITY)
- ⚠️ `confirm_payment_details` - **NEEDS INTEGRATION**

### 5. **Information** (LOW PRIORITY)
- ✅ `request_update_or_cancel` - **WORKING** (sends email)
- ❓ `general_info` - Can be handled by AI with hardcoded data
- ❓ `location_info` - Can send WhatsApp location message

---

## ❌ What Maldevta DOESN'T Need

### 1. **Hourly Bookings**
- ❌ `check_hourly_availability`
- ❌ `create_hourly_booking_reservation`
- ❌ `get_hourly_booking_by_id`

**Reason:** Maldevta Farms doesn't offer hourly room bookings

### 2. **Day Outing** (MAYBE)
- ❓ `create_day_outing_reservation`
- ❓ `get_all_day_outing_reservations`

**Question:** Does Maldevta offer day outing packages? If not, remove these.

---

## 🔧 Current Integration Status

### Travel Studio API (Working)
✅ **Integrated and tested:**
- `check_availability` → `get_available_rooms()`
- `get_bookings()` → Can be used for `get_all_room_reservations`
- `create_booking()` → Ready to use for `create_booking_reservation`
- Multi-room bookings
- Room extensions
- Room upgrades
- Add/remove/update rooms

### Vercel API (Broken)
❌ **Still using but NOT working:**
- All endpoints except `check_availability`
- Returns 404 errors
- Deployment doesn't exist

---

## 📋 Action Items

### IMMEDIATE (Must Fix)

#### 1. Create Room Booking via Travel Studio
**Current:** `create_booking_reservation()` calls broken Vercel endpoint

**Fix:** Update to use Travel Studio's `create_booking()` method

```python
async def create_booking_reservation(self, params: Dict[str, Any]) -> Dict[str, Any]:
    # Use Travel Studio API
    result = self.travel_studio.create_booking(
        guest_name=params['name'],
        guest_email=params.get('email', ''),
        guest_phone=params['phone_number'],
        check_in_date=params['check_in'],
        check_out_date=params['check_out'],
        room_type=params['room_type_ids'][0],
        number_of_guests=params['num_of_adults'] + params.get('num_of_children', 0),
        special_requests=params.get('special_request')
    )
    return result
```

#### 2. Get Bookings via Travel Studio
**Current:** `get_all_room_reservations()` calls broken Vercel endpoint

**Fix:** Use Travel Studio's `get_bookings()` method

```python
async def get_all_room_reservations(self, params: Dict[str, Any]) -> Dict[str, Any]:
    bookings = self.travel_studio.get_bookings()
    return {"success": True, "data": bookings}
```

---

### MEDIUM PRIORITY

#### 3. Event Inquiries
**Options:**
1. Use Travel Studio if it has event management
2. Send email to owner (like `request_update_or_cancel`)
3. Store in database

**Recommendation:** Send email (simplest for now)

#### 4. Lead Generation
**Options:**
1. Store in database
2. Send email to owner
3. Integrate with CRM

**Recommendation:** Send email (simplest for now)

#### 5. Payment Confirmation
**Options:**
1. Integrate with Travel Studio payment system
2. Manual verification (email notification)

**Recommendation:** Check Travel Studio API for payment endpoints

---

### LOW PRIORITY

#### 6. General Info
**Current:** Calls Vercel endpoint

**Fix:** Return hardcoded hotel information

```python
async def general_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "success": True,
        "data": {
            "name": "Maldevta Farms",
            "location": "Maldevta, Dehradun",
            "amenities": ["Pool", "Garden", "Cottages"],
            "check_in": "2:00 PM",
            "check_out": "11:00 AM"
        }
    }
```

#### 7. Location Info
**Current:** Calls Vercel endpoint

**Fix:** Send WhatsApp location message directly

```python
async def location_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
    # Send location via WhatsApp API
    whatsapp_service = WhatsAppService()
    whatsapp_service.send_location(
        to=params['phone_number'],
        latitude=30.1234,
        longitude=78.5678,
        name="Maldevta Farms",
        address="Maldevta, Dehradun"
    )
    return {"success": True}
```

---

## 🎯 Recommended Implementation Order

### Phase 1: Critical Booking Functions (Week 1)
1. ✅ `check_availability` - **DONE**
2. 🔄 `create_booking_reservation` - Integrate with Travel Studio
3. 🔄 `get_all_room_reservations` - Use Travel Studio
4. 🔄 Test complete booking flow

### Phase 2: Additional Features (Week 2)
5. 🔄 `create_event_inquiry` - Email to owner
6. 🔄 `lead_gen` - Email to owner
7. 🔄 `human_followup` - Email to owner
8. ✅ `request_update_or_cancel` - **DONE**

### Phase 3: Nice-to-Have (Week 3)
9. 🔄 `confirm_payment_details` - Check Travel Studio
10. 🔄 `general_info` - Hardcode hotel data
11. 🔄 `location_info` - WhatsApp location
12. 🔄 Remove hourly booking functions (not needed)
13. 🔄 Remove/decide on day outing functions

---

## 📊 Summary Table

| Category | Endpoints Needed | Priority | Status |
|----------|-----------------|----------|---------|
| **Availability** | 1 | HIGH | ✅ Done |
| **Room Booking** | 2 | HIGH | ⚠️ 1 Done, 1 Pending |
| **Event Management** | 2 | HIGH | ⚠️ Pending |
| **Lead & Follow-up** | 2 | MEDIUM | ⚠️ Pending |
| **Payment** | 1 | MEDIUM | ⚠️ Pending |
| **Information** | 2 | LOW | ⚠️ Pending |
| **Hourly Booking** | 3 | N/A | ❌ Not Needed |
| **Day Outing** | 2 | N/A | ❓ To Decide |

---

## 🔑 Key Decisions Needed

### 1. Does Maldevta offer day outings?
- [ ] YES → Keep day outing endpoints, integrate with Travel Studio/Email
- [ ] NO → Remove day outing endpoints from tool_service.py

### 2. Event inquiry handling?
- [ ] Use Travel Studio (if available)
- [ ] Send email to owner (simple)
- [ ] Store in database (complex)

### 3. Lead generation storage?
- [ ] Database (recommended)
- [ ] Email only (simple)
- [ ] CRM integration (future)

### 4. Payment verification?
- [ ] Travel Studio integration (if available)
- [ ] Manual (email notification)
- [ ] Third-party payment gateway

---

## 📞 Next Steps

1. **Immediate:** Implement `create_booking_reservation` with Travel Studio
2. **Immediate:** Implement `get_all_room_reservations` with Travel Studio
3. **Decide:** Day outing - needed or not?
4. **Decide:** Event inquiry - Travel Studio or email?
5. **Decide:** Lead gen - database or email?

---

**Date:** December 8, 2025  
**Status:** Analysis Complete  
**Next Action:** Implement Phase 1 (Critical Booking Functions)
