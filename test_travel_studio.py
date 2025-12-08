"""
Test script for Travel Studio API integration
"""

import asyncio
from services import get_travel_studio_service
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_connection():
    """Test basic connection to Travel Studio API"""
    logger.info("Testing Travel Studio API connection...")
    
    service = get_travel_studio_service()
    
    if not service.client_initialized:
        logger.error("Service not initialized - check TRAVEL_STUDIO_BEARER_TOKEN")
        return False
    
    logger.info(f"Service initialized with base URL: {service.base_url}")
    return True


def test_get_hotel_profile():
    """Test getting hotel profile"""
    logger.info("\n=== Testing Get Hotel Profile ===")
    
    service = get_travel_studio_service()
    profile = service.get_hotel_profile()
    
    if profile:
        logger.info(f"Hotel Profile: {profile}")
        return True
    else:
        logger.error("Failed to get hotel profile")
        return False


def test_get_bookings():
    """Test getting bookings"""
    logger.info("\n=== Testing Get Bookings ===")
    
    service = get_travel_studio_service()
    bookings = service.get_bookings()
    
    if bookings is not None:
        logger.info(f"Found {len(bookings)} bookings")
        if bookings:
            logger.info(f"First booking: {bookings[0]}")
        return True
    else:
        logger.error("Failed to get bookings")
        return False


def test_get_room_types():
    """Test getting room types"""
    logger.info("\n=== Testing Get Room Types ===")
    
    service = get_travel_studio_service()
    room_types = service.get_room_types()
    
    if room_types is not None:
        logger.info(f"Found {len(room_types)} room types")
        for room in room_types:
            logger.info(f"Room: {room}")
        return True
    else:
        logger.error("Failed to get room types")
        return False


def test_create_booking():
    """Test creating a booking (will likely need actual room data)"""
    logger.info("\n=== Testing Create Booking ===")
    
    service = get_travel_studio_service()
    
    booking = service.create_booking(
        guest_name="Test Guest",
        guest_email="test@example.com",
        guest_phone="9999999999",
        check_in_date="2025-12-15",
        check_out_date="2025-12-17",
        room_type="Deluxe",
        number_of_guests=2,
        special_requests="Late check-in"
    )
    
    if booking:
        logger.info(f"Booking created: {booking}")
        return True
    else:
        logger.warning("Failed to create booking (this is expected if test data is invalid)")
        return False


def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("Starting Travel Studio API Integration Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Connection", test_connection),
        ("Hotel Profile", test_get_hotel_profile),
        ("Get Bookings", test_get_bookings),
        ("Room Types", test_get_room_types),
        ("Create Booking", test_create_booking),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test '{test_name}' failed with exception: {str(e)}")
            results.append((test_name, False))
    
    logger.info("\n" + "=" * 60)
    logger.info("Test Results Summary")
    logger.info("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
