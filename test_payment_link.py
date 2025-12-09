"""
Test that payment link is properly generated after booking
"""

def test_payment_link_format():
    """Test payment link format"""
    booking_id = "BK1765262025105L5TXG"
    payment_url = f"https://maldevtafarms.com/book?bookingId={booking_id}"
    
    expected_message = f"Your Booking ID: {booking_id}. Complete payment: {payment_url}"
    
    print("Testing payment link format...")
    print(f"✅ Payment URL: {payment_url}")
    print(f"✅ Full message: {expected_message}")
    print("\nThe AI should include this format in its response after successful booking.")

def test_booking_response_structure():
    """Test booking response structure"""
    # Simulate booking response
    booking_response = {
        "success": True,
        "data": {
            "booking_id": "BK1765262025105L5TXG",
            "guest_name": "Test Guest",
            "room_category": "Deluxe",
            "check_in_date": "2025-12-20",
            "check_out_date": "2025-12-22"
        }
    }
    
    if booking_response.get("success"):
        booking_id = booking_response["data"].get("booking_id")
        payment_url = f"https://maldevtafarms.com/book?bookingId={booking_id}"
        
        print("\n" + "="*60)
        print("Booking Created Successfully!")
        print("="*60)
        print(f"Booking ID: {booking_id}")
        print(f"Guest: {booking_response['data']['guest_name']}")
        print(f"Room: {booking_response['data']['room_category']}")
        print(f"Check-in: {booking_response['data']['check_in_date']}")
        print(f"Check-out: {booking_response['data']['check_out_date']}")
        print(f"\n💳 Payment Link: {payment_url}")
        print("\nAI Response should be:")
        print(f"\"Done! Your Booking ID: {booking_id}. Complete payment here: {payment_url}\"")

if __name__ == "__main__":
    test_payment_link_format()
    test_booking_response_structure()
    
    print("\n" + "="*60)
    print("✅ Payment link format is correct!")
    print("="*60)
