"""
Simple test of Travel Studio API without dependencies
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net"
TOKEN = os.getenv("TRAVEL_STUDIO_BEARER_TOKEN")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

print("=" * 60)
print("Testing Travel Studio API Connection")
print("=" * 60)
print(f"Base URL: {BASE_URL}")
print(f"Token configured: {bool(TOKEN)}")
print()

# Test various common endpoints
endpoints_to_test = [
    "/api/hotel/bookings",
    "/api/hotel/profile",
    "/api/hotel/rooms/types",
    "/api/bookings",
    "/hotel/bookings",
    "/bookings",
]

for endpoint in endpoints_to_test:
    try:
        url = f"{BASE_URL}{endpoint}"
        print(f"Testing: GET {endpoint}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Success: {data}")
        else:
            print(f"  Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
    print()

print("=" * 60)
print("If you see '404 Route not found' for all endpoints,")
print("you'll need to check the API documentation for correct endpoints.")
print("=" * 60)
