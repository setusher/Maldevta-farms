# Testing Guide - Travel Studio API Endpoints

## Quick Test Commands

### 1. Test with Python Script (Recommended)

```bash
python test_travel_api.py
```

This tests multiple common endpoint patterns automatically.

### 2. Test with curl

Basic syntax:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/ENDPOINT
```

### 3. Test Specific Endpoints

#### Test Root Endpoint
```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJob3RlbElkIjoiYWVjOTNlYWItYTE3Yi00YmVjLWI0NGEtMDgwMzBkZWFkNTRmIiwiZW1haWwiOiJkcmRAZ21haWwuY29tIiwicm9sZSI6ImhvdGVsIiwiaWF0IjoxNzY0NjY1MTM0LCJleHAiOjE3NjUyNjk5MzR9.ga5XUbkfj1WduHx5965wUXdFUhaebVoEw4j_uM9tCCY" \
     https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/
```

#### Test Bookings Endpoint
```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJob3RlbElkIjoiYWVjOTNlYWItYTE3Yi00YmVjLWI0NGEtMDgwMzBkZWFkNTRmIiwiZW1haWwiOiJkcmRAZ21haWwuY29tIiwicm9sZSI6ImhvdGVsIiwiaWF0IjoxNzY0NjY1MTM0LCJleHAiOjE3NjUyNjk5MzR9.ga5XUbkfj1WduHx5965wUXdFUhaebVoEw4j_uM9tCCY" \
     https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/api/bookings
```

#### Test with Verbose Output (See Full Request/Response)
```bash
curl -v \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJob3RlbElkIjoiYWVjOTNlYWItYTE3Yi00YmVjLWI0NGEtMDgwMzBkZWFkNTRmIiwiZW1haWwiOiJkcmRAZ21haWwuY29tIiwicm9sZSI6ImhvdGVsIiwiaWF0IjoxNzY0NjY1MTM0LCJleHAiOjE3NjUyNjk5MzR9.ga5XUbkfj1WduHx5965wUXdFUhaebVoEw4j_uM9tCCY" \
     -H "Content-Type: application/json" \
     https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/api/hotel/profile
```

#### Test POST Request (Create Booking)
```bash
curl -X POST \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJob3RlbElkIjoiYWVjOTNlYWItYTE3Yi00YmVjLWI0NGEtMDgwMzBkZWFkNTRmIiwiZW1haWwiOiJkcmRAZ21haWwuY29tIiwicm9sZSI6ImhvdGVsIiwiaWF0IjoxNzY0NjY1MTM0LCJleHAiOjE3NjUyNjk5MzR9.ga5XUbkfj1WduHx5965wUXdFUhaebVoEw4j_uM9tCCY" \
     -H "Content-Type: application/json" \
     -d '{
       "guest_name": "Test User",
       "guest_email": "test@example.com",
       "guest_phone": "9999999999",
       "check_in_date": "2025-12-15",
       "check_out_date": "2025-12-17",
       "room_type": "Deluxe",
       "number_of_guests": 2
     }' \
     https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/api/bookings
```

## 4. Test with Postman or Insomnia

### Setup in Postman:

1. **Create a new request**
2. **Set Method**: GET or POST
3. **Set URL**: `https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/your-endpoint`
4. **Add Headers**:
   - Key: `Authorization`
   - Value: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJob3RlbElkIjoiYWVjOTNlYWItYTE3Yi00YmVjLWI0NGEtMDgwMzBkZWFkNTRmIiwiZW1haWwiOiJkcmRAZ21haWwuY29tIiwicm9sZSI6ImhvdGVsIiwiaWF0IjoxNzY0NjY1MTM0LCJleHAiOjE3NjUyNjk5MzR9.ga5XUbkfj1WduHx5965wUXdFUhaebVoEw4j_uM9tCCY`
   - Key: `Content-Type`
   - Value: `application/json`
5. **Send Request**

### Postman Collection JSON

Save this as `travel_studio_api.postman_collection.json`:

```json
{
  "info": {
    "name": "Travel Studio API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJob3RlbElkIjoiYWVjOTNlYWItYTE3Yi00YmVjLWI0NGEtMDgwMzBkZWFkNTRmIiwiZW1haWwiOiJkcmRAZ21haWwuY29tIiwicm9sZSI6ImhvdGVsIiwiaWF0IjoxNzY0NjY1MTM0LCJleHAiOjE3NjUyNjk5MzR9.ga5XUbkfj1WduHx5965wUXdFUhaebVoEw4j_uM9tCCY"
      }
    ]
  },
  "item": [
    {
      "name": "Get Bookings",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/api/hotel/bookings",
          "protocol": "https",
          "host": ["travel-studio-backend-e2bkc2e0a8e4e3hy", "centralindia-01", "azurewebsites", "net"],
          "path": ["api", "hotel", "bookings"]
        }
      }
    },
    {
      "name": "Get Hotel Profile",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/api/hotel/profile",
          "protocol": "https",
          "host": ["travel-studio-backend-e2bkc2e0a8e4e3hy", "centralindia-01", "azurewebsites", "net"],
          "path": ["api", "hotel", "profile"]
        }
      }
    }
  ]
}
```

## 5. Test Your Local Server Endpoints

Once your FastAPI server is running:

```bash
# Start server
python server.py

# In another terminal, test your endpoints:

# Get bookings
curl http://localhost:8000/travel-studio/bookings

# Get hotel profile
curl http://localhost:8000/travel-studio/profile

# Get room types
curl http://localhost:8000/travel-studio/rooms/types

# Check availability
curl "http://localhost:8000/travel-studio/rooms/available?check_in_date=2025-12-15&check_out_date=2025-12-17"
```

## 6. Interactive Testing with HTTPie (Recommended)

Install HTTPie:
```bash
pip install httpie
```

Test endpoints:
```bash
# Simple GET
http https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/api/hotel/bookings \
  "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# POST with JSON
http POST https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/api/bookings \
  "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  guest_name="John Doe" \
  guest_email="john@example.com" \
  check_in_date="2025-12-15"
```

## Common Endpoint Patterns to Try

Based on typical hotel booking APIs, try these patterns:

```bash
# Authentication/Profile
GET /api/auth/profile
GET /api/hotel/profile
GET /api/me

# Bookings
GET /api/bookings
GET /api/hotel/bookings
GET /api/reservations
POST /api/bookings
POST /api/reservations

# Rooms
GET /api/rooms
GET /api/hotel/rooms
GET /api/rooms/available
GET /api/availability

# Guests
GET /api/guests
GET /api/hotel/guests
GET /api/customers
```

## Debugging Tips

### 1. Check Token Expiration
Your token expires on **February 8, 2025**. Check if it's still valid:

```bash
# Decode JWT token (paste at jwt.io)
# Or use this command:
echo "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJob3RlbElkIjoiYWVjOTNlYWItYTE3Yi00YmVjLWI0NGEtMDgwMzBkZWFkNTRmIiwiZW1haWwiOiJkcmRAZ21haWwuY29tIiwicm9sZSI6ImhvdGVsIiwiaWF0IjoxNzY0NjY1MTM0LCJleHAiOjE3NjUyNjk5MzR9" | base64 -d
```

Result:
```json
{
  "hotelId": "aec93eab-a17b-4bec-b44a-08030dead54f",
  "email": "drd@gmail.com",
  "role": "hotel",
  "iat": 1764665134,
  "exp": 1765269934
}
```

### 2. Check Response Headers
```bash
curl -I -H "Authorization: Bearer YOUR_TOKEN" \
     https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/
```

### 3. Test Without Authentication
```bash
# See if any endpoints are public
curl https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/
curl https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/health
curl https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/docs
curl https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/api
```

### 4. Save Response to File
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/api/bookings \
     -o response.json
```

## What to Look For

### Success Responses (200-299)
- Status code: 200, 201, 202
- JSON response with data
- No error messages

### Client Errors (400-499)
- 400: Bad Request - Check your JSON format
- 401: Unauthorized - Check token
- 403: Forbidden - Check permissions
- 404: Not Found - Endpoint doesn't exist
- 422: Validation Error - Check required fields

### Server Errors (500-599)
- 500: Internal Server Error
- 502: Bad Gateway
- 503: Service Unavailable

## Creating Your Own Test Script

Here's a template for testing custom endpoints:

```python
import requests
import json

BASE_URL = "https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

def test_endpoint(method, endpoint, data=None):
    """Test any endpoint"""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        print(f"{method} {endpoint}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        print("-" * 60)
        
        return response
        
    except Exception as e:
        print(f"Error: {e}")
        return None

# Test your endpoints
test_endpoint("GET", "/")
test_endpoint("GET", "/api/bookings")
test_endpoint("GET", "/api/hotel/profile")

# Test POST
test_endpoint("POST", "/api/bookings", {
    "guest_name": "Test User",
    "check_in_date": "2025-12-15",
    "check_out_date": "2025-12-17"
})
```

## Need the API Documentation?

Contact the Travel Studio team and ask for:

1. **API Documentation URL** (e.g., Swagger/OpenAPI docs)
2. **List of available endpoints**
3. **Request/response examples**
4. **Authentication requirements**
5. **Rate limits and quotas**

Common documentation URLs to try:
```bash
# OpenAPI/Swagger docs
curl https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/docs
curl https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/swagger
curl https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/api-docs
curl https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/openapi.json
```
