# Travel Studio API Integration

This document describes the integration with the Travel Studio Backend API for hotel booking management.

## Configuration

Add the following environment variables to your `.env` file:

```bash
TRAVEL_STUDIO_API_URL="https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net"
TRAVEL_STUDIO_BEARER_TOKEN="your_bearer_token_here"
```

The bearer token has been configured with:
- Hotel ID: `aec93eab-a17b-4bec-b44a-08030dead54f`
- Role: `hotel`
- Expiration: 2025-02-08

## Service Overview

The `TravelStudioService` class provides a complete interface to interact with the Travel Studio API. It handles:

- **Booking Management**: Create, retrieve, update, and cancel bookings
- **Room Management**: Check availability and get room types
- **Guest Management**: Retrieve guest information and booking history
- **Analytics**: Get occupancy and revenue reports
- **Hotel Profile**: Manage hotel information

## Usage Examples

### 1. Initialize the Service

```python
from services import get_travel_studio_service

# Get singleton instance
travel_studio = get_travel_studio_service()
```

### 2. Get All Bookings

```python
# Get all bookings
bookings = travel_studio.get_bookings()

# Filter by status
pending_bookings = travel_studio.get_bookings(status="pending")

# Filter by date range
bookings = travel_studio.get_bookings(
    start_date="2025-12-01",
    end_date="2025-12-31"
)
```

### 3. Get a Specific Booking

```python
booking = travel_studio.get_booking_by_id("booking_123")
if booking:
    print(f"Guest: {booking['guest_name']}")
    print(f"Check-in: {booking['check_in_date']}")
```

### 4. Create a New Booking

```python
booking = travel_studio.create_booking(
    guest_name="John Doe",
    guest_email="john@example.com",
    guest_phone="9999999999",
    check_in_date="2025-12-15",
    check_out_date="2025-12-17",
    room_type="Deluxe",
    number_of_guests=2,
    special_requests="Late check-in please"
)

if booking:
    print(f"Booking created with ID: {booking['id']}")
```

### 5. Update a Booking

```python
updated_booking = travel_studio.update_booking(
    booking_id="booking_123",
    check_out_date="2025-12-18",
    special_requests="Early check-out"
)
```

### 6. Cancel a Booking

```python
success = travel_studio.cancel_booking(
    booking_id="booking_123",
    reason="Guest requested cancellation"
)
```

### 7. Confirm a Booking

```python
success = travel_studio.confirm_booking("booking_123")
```

### 8. Check Room Availability

```python
available_rooms = travel_studio.get_available_rooms(
    check_in_date="2025-12-15",
    check_out_date="2025-12-17",
    room_type="Deluxe"  # Optional filter
)

for room in available_rooms:
    print(f"Room: {room['name']} - Price: {room['price']}")
```

### 9. Get Room Types

```python
room_types = travel_studio.get_room_types()

for room_type in room_types:
    print(f"{room_type['name']}: {room_type['description']}")
```

### 10. Get Guest Information

```python
# By phone number
guest = travel_studio.get_guest_by_phone("9999999999")

# Get guest's booking history
guest_bookings = travel_studio.get_guest_bookings("9999999999")
```

### 11. Get Reports

```python
# Occupancy report
occupancy = travel_studio.get_occupancy_report(
    start_date="2025-12-01",
    end_date="2025-12-31"
)

# Revenue report
revenue = travel_studio.get_revenue_report(
    start_date="2025-12-01",
    end_date="2025-12-31"
)
```

### 12. Hotel Profile Management

```python
# Get hotel profile
profile = travel_studio.get_hotel_profile()

# Update hotel profile
updated_profile = travel_studio.update_hotel_profile(
    name="Updated Hotel Name",
    description="New description",
    amenities=["WiFi", "Pool", "Gym"]
)
```

## API Endpoints

The server exposes the following endpoints for the Travel Studio integration:

### GET `/travel-studio/bookings`
Get all bookings with optional filters.

**Query Parameters:**
- `status` (optional): Filter by booking status
- `start_date` (optional): Filter from date (YYYY-MM-DD)
- `end_date` (optional): Filter to date (YYYY-MM-DD)

**Example:**
```bash
curl http://localhost:8000/travel-studio/bookings?status=pending
```

### GET `/travel-studio/bookings/{booking_id}`
Get a specific booking by ID.

**Example:**
```bash
curl http://localhost:8000/travel-studio/bookings/booking_123
```

### POST `/travel-studio/bookings`
Create a new booking.

**Request Body:**
```json
{
  "guest_name": "John Doe",
  "guest_email": "john@example.com",
  "guest_phone": "9999999999",
  "check_in_date": "2025-12-15",
  "check_out_date": "2025-12-17",
  "room_type": "Deluxe",
  "number_of_guests": 2,
  "special_requests": "Late check-in"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/travel-studio/bookings \
  -H "Content-Type: application/json" \
  -d '{"guest_name":"John Doe","guest_email":"john@example.com","guest_phone":"9999999999","check_in_date":"2025-12-15","check_out_date":"2025-12-17","room_type":"Deluxe","number_of_guests":2}'
```

### GET `/travel-studio/rooms/available`
Get available rooms for given dates.

**Query Parameters:**
- `check_in_date` (required): Check-in date (YYYY-MM-DD)
- `check_out_date` (required): Check-out date (YYYY-MM-DD)
- `room_type` (optional): Filter by room type

**Example:**
```bash
curl "http://localhost:8000/travel-studio/rooms/available?check_in_date=2025-12-15&check_out_date=2025-12-17"
```

### GET `/travel-studio/rooms/types`
Get all room types.

**Example:**
```bash
curl http://localhost:8000/travel-studio/rooms/types
```

### GET `/travel-studio/profile`
Get hotel profile information.

**Example:**
```bash
curl http://localhost:8000/travel-studio/profile
```

## Testing

Run the test script to verify the integration:

```bash
python test_travel_studio.py
```

The test script will:
1. Test API connection
2. Fetch hotel profile
3. Get existing bookings
4. Retrieve room types
5. Attempt to create a test booking

## Error Handling

The service includes comprehensive error handling:

- All methods return `None` or `False` on error
- Errors are logged with detailed information
- HTTP errors include status codes and response bodies
- Network timeouts are set to 30 seconds

## Integration with WhatsApp Agent

You can integrate the Travel Studio service with your WhatsApp agent to:

1. **Check availability**: When guests ask about room availability
2. **Create bookings**: When guests want to make a reservation
3. **Retrieve bookings**: When guests ask about their booking status
4. **Modify bookings**: When guests need to change dates or cancel

### Example Agent Integration

```python
from services import get_travel_studio_service

async def handle_booking_request(guest_phone, check_in, check_out, room_type):
    travel_studio = get_travel_studio_service()
    
    # Check availability
    available_rooms = travel_studio.get_available_rooms(
        check_in_date=check_in,
        check_out_date=check_out,
        room_type=room_type
    )
    
    if not available_rooms:
        return "Sorry, no rooms available for those dates."
    
    # Create booking
    booking = travel_studio.create_booking(
        guest_name="Guest Name",
        guest_email="guest@example.com",
        guest_phone=guest_phone,
        check_in_date=check_in,
        check_out_date=check_out,
        room_type=room_type,
        number_of_guests=2
    )
    
    if booking:
        return f"Booking confirmed! Your booking ID is {booking['id']}"
    else:
        return "Sorry, we couldn't complete your booking. Please try again."
```

## API Authentication

All requests to the Travel Studio API are authenticated using a Bearer token:

```
Authorization: Bearer {token}
```

The token is automatically included in all requests by the service.

## Token Expiration

The current token expires on **2025-02-08**. When the token expires, you'll need to:

1. Request a new token from the Travel Studio API
2. Update the `TRAVEL_STUDIO_BEARER_TOKEN` in your `.env` file

## Support

For issues or questions about the Travel Studio API integration, contact the development team.
