"""
Travel Studio API Integration Service
Handles all interactions with the Travel Studio Backend API
"""

import os
import logging
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class TravelStudioService:
    def __init__(self):
        """Initialize Travel Studio API service"""
        self.base_url = os.getenv(
            "TRAVEL_STUDIO_API_URL",
            "https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net"
        )
        self.bearer_token = os.getenv("TRAVEL_STUDIO_BEARER_TOKEN")
        
        if not self.bearer_token:
            logger.warning("TRAVEL_STUDIO_BEARER_TOKEN not set in environment")
            self.client_initialized = False
        else:
            self.client_initialized = True
            logger.info(f"Travel Studio API service initialized with base URL: {self.base_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Make HTTP request to Travel Studio API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            
        Returns:
            Response data as dictionary or None on error
        """
        if not self.client_initialized:
            logger.error("Travel Studio API client not initialized")
            return None
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.info(f"Making {method} request to {url}")
            
            response = requests.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                json=data,
                params=params,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Request successful: {response.status_code}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in API request: {str(e)}")
            return None
    
    # Booking Management
    
    def get_bookings(
        self, 
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[List[Dict]]:
        """
        Get all bookings for the hotel
        
        Args:
            status: Filter by booking status (pending, confirmed, cancelled, completed)
            start_date: Filter bookings from this date (YYYY-MM-DD)
            end_date: Filter bookings until this date (YYYY-MM-DD)
            
        Returns:
            List of booking objects or None on error
        """
        params = {}
        if status:
            params['status'] = status
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        result = self._make_request("GET", "/api/hocc/bookings", params=params)
        
        if result and result.get("success"):
            return result.get("data", {}).get("items", [])
        return None
    
    def get_booking_by_id(self, booking_id: str) -> Optional[Dict]:
        """
        Get a specific booking by ID
        
        Args:
            booking_id: Booking ID
            
        Returns:
            Booking object or None on error
        """
        result = self._make_request("GET", f"/api/hocc/bookings/{booking_id}")
        
        if result and result.get("success"):
            return result.get("data")
        return None
    
    def create_booking(
        self,
        guest_name: str,
        guest_email: str,
        guest_phone: str,
        check_in_date: str,
        check_out_date: str,
        room_category: str,
        num_adults: int,
        num_children: int = 0,
        num_nights: Optional[int] = None,
        booking_channel: str = "whatsapp",
        payment_status: str = "Unpaid",
        special_requests: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict]:
        """
        Create a new booking
        
        Args:
            guest_name: Guest full name
            guest_email: Guest email
            guest_phone: Guest phone number (format: +11234567890)
            check_in_date: Check-in date (ISO format: YYYY-MM-DDTHH:MM:SS.SSSZ or YYYY-MM-DD)
            check_out_date: Check-out date (ISO format: YYYY-MM-DDTHH:MM:SS.SSSZ or YYYY-MM-DD)
            room_category: Room category (e.g., "Deluxe", "Luxury Cottage")
            num_adults: Number of adults
            num_children: Number of children (default: 0)
            num_nights: Number of nights (calculated if not provided)
            booking_channel: Booking source (default: "whatsapp")
            payment_status: Payment status (default: "Unpaid")
            special_requests: Any special requests
            **kwargs: Additional booking details
            
        Returns:
            Created booking object or None on error
            
        Example Request:
            {
                "guest_name": "John Doe",
                "guest_phone": "+11234567890",
                "guest_email": "john.doe@example.com",
                "room_category": "Deluxe",
                "num_adults": 2,
                "num_children": 1,
                "check_in_date": "2025-12-01T14:00:00.000Z",
                "num_nights": 3,
                "check_out_date": "2025-12-04T10:00:00.000Z",
                "booking_channel": "whatsapp",
                "payment_status": "Unpaid"
            }
        """
        from datetime import datetime
        
        try:
            # Convert YYYY-MM-DD to ISO format if needed
            if "T" not in check_in_date:
                check_in_date = f"{check_in_date}T14:00:00.000Z"
            if "T" not in check_out_date:
                check_out_date = f"{check_out_date}T10:00:00.000Z"
            
            # Calculate num_nights if not provided
            if num_nights is None:
                checkin = datetime.fromisoformat(check_in_date.replace('Z', '+00:00'))
                checkout = datetime.fromisoformat(check_out_date.replace('Z', '+00:00'))
                num_nights = (checkout - checkin).days
            
            data = {
                "guest_name": guest_name,
                "guest_phone": guest_phone,
                "guest_email": guest_email,
                "room_category": room_category,
                "num_adults": num_adults,
                "num_children": num_children,
                "check_in_date": check_in_date,
                "num_nights": num_nights,
                "check_out_date": check_out_date,
                "booking_channel": booking_channel,
                "payment_status": payment_status,
                **kwargs
            }
            
            if special_requests:
                data["special_requests"] = special_requests
            
            result = self._make_request("POST", "/api/hocc/bookings", data=data)
            
            if result and result.get("success"):
                logger.info(f"Booking created successfully: {result.get('data', {}).get('booking_id')}")
                return result.get("data")
            return None
            
        except Exception as e:
            logger.error(f"Error creating booking: {str(e)}", exc_info=True)
            return None
    
    def update_booking(
        self,
        booking_id: str,
        **update_fields
    ) -> Optional[Dict]:
        """
        Update an existing booking
        
        Args:
            booking_id: Booking ID to update
            **update_fields: Fields to update
            
        Returns:
            Updated booking object or None on error
        """
        result = self._make_request(
            "PUT", 
            f"/api/hocc/bookings/{booking_id}",
            data=update_fields
        )
        
        if result and result.get("success"):
            logger.info(f"Booking {booking_id} updated successfully")
            return result.get("data")
        return None
    
    def cancel_booking(self, booking_id: str, reason: Optional[str] = None) -> bool:
        """
        Cancel a booking
        
        Args:
            booking_id: Booking ID to cancel
            reason: Cancellation reason
            
        Returns:
            True if successful, False otherwise
        """
        data = {"reason": reason} if reason else {}
        result = self._make_request(
            "POST",
            f"/api/hocc/bookings/{booking_id}/cancel",
            data=data
        )
        
        if result and result.get("success"):
            logger.info(f"Booking {booking_id} cancelled successfully")
            return True
        return False
    
    def confirm_booking(self, booking_id: str) -> bool:
        """
        Confirm a booking
        
        Args:
            booking_id: Booking ID to confirm
            
        Returns:
            True if successful, False otherwise
        """
        result = self._make_request(
            "POST",
            f"/api/hocc/bookings/{booking_id}/confirm"
        )
        
        if result and result.get("success"):
            logger.info(f"Booking {booking_id} confirmed successfully")
            return True
        return False
    
    # Room Management
    
    def get_all_rooms(self) -> Optional[List[Dict]]:
        """
        Get all rooms in the hotel
        
        Returns:
            List of all rooms or None on error
        """
        result = self._make_request("GET", "/api/hocc/rooms")
        
        if result and result.get("success"):
            return result.get("data", {}).get("items", [])
        return None
    
    def get_available_rooms(
        self,
        check_in_date: str,
        check_out_date: str,
        category: Optional[str] = None,
        num_adults: Optional[int] = None,
        num_children: Optional[int] = None
    ) -> Optional[List[Dict]]:
        """
        Get available rooms for given dates using the Travel Studio API
        
        Args:
            check_in_date: Check-in date (ISO format: YYYY-MM-DDTHH:MM:SS.SSSZ or YYYY-MM-DD)
            check_out_date: Check-out date (ISO format: YYYY-MM-DDTHH:MM:SS.SSSZ or YYYY-MM-DD)
            category: Filter by room category (optional, e.g., "Deluxe", "Luxury Cottage")
            num_adults: Number of adults (optional)
            num_children: Number of children (optional)
            
        Returns:
            List of available rooms with pricing or None on error
            
        Example Response:
            [
                {
                    "id": "683635a0-7b97-4dd2-900f-cc3e67738870",
                    "roomNumber": "012",
                    "category": "Deluxe",
                    "floor": "1",
                    "wing": "A",
                    "isOccupiable": true,
                    "booking_list": [...],
                    "image_urls": [],
                    "base_rate": "5775.00",
                    "status": "vacant"
                }
            ]
        """
        try:
            # Convert YYYY-MM-DD to ISO format if needed
            if "T" not in check_in_date:
                check_in_date = f"{check_in_date}T14:00:00.000Z"
            if "T" not in check_out_date:
                check_out_date = f"{check_out_date}T11:00:00.000Z"
            
            # Build request body
            data = {
                "check_in_date": check_in_date,
                "check_out_date": check_out_date
            }
            
            if category:
                data["category"] = category
            
            # Make POST request to /api/hocc/rooms/available
            result = self._make_request("POST", "/api/hocc/rooms/available", data=data)
            
            if result and result.get("success"):
                available_rooms = result.get("data", [])
                logger.info(f"Found {len(available_rooms)} available rooms for category '{category}' from {check_in_date} to {check_out_date}")
                return available_rooms
            else:
                logger.warning(f"No available rooms found or API error")
                return None
            
        except Exception as e:
            logger.error(f"Error checking room availability: {str(e)}", exc_info=True)
            return None
    
    def get_room_types(self) -> Optional[List[str]]:
        """
        Get all room types/categories from available rooms
        
        Returns:
            List of unique room categories or None on error
        """
        rooms = self.get_all_rooms()
        if not rooms:
            return None
        
        # Extract unique categories
        categories = list(set(room.get("category") for room in rooms if room.get("category")))
        return sorted(categories)
    
    def get_room_bookings(self, room_id: str) -> Optional[List[Dict]]:
        """
        Get all bookings for a specific room
        
        Args:
            room_id: Room ID (UUID format)
            
        Returns:
            List of bookings for the room or None on error
            
        Example Endpoint:
            GET /api/hocc/rooms/{room_id}/bookings
        """
        result = self._make_request("GET", f"/api/hocc/rooms/{room_id}/bookings")
        
        if result and result.get("success"):
            return result.get("data", [])
        return None
    
    # Guest Management
    
    def get_guest_by_phone(self, phone: str) -> Optional[Dict]:
        """
        Get guest information by phone number
        
        Args:
            phone: Guest phone number
            
        Returns:
            Guest object or None if not found
        """
        result = self._make_request("GET", f"/api/hocc/guests/phone/{phone}")
        
        if result and result.get("success"):
            return result.get("data")
        return None
    
    def get_guest_bookings(self, phone: str) -> Optional[List[Dict]]:
        """
        Get all bookings for a guest by phone number
        
        Args:
            phone: Guest phone number
            
        Returns:
            List of bookings or None on error
        """
        result = self._make_request("GET", f"/api/hocc/guests/phone/{phone}/bookings")
        
        if result and result.get("success"):
            return result.get("data", {}).get("items", [])
        return None
    
    # Analytics & Reports
    
    def get_occupancy_report(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get occupancy report
        
        Args:
            start_date: Report start date (YYYY-MM-DD)
            end_date: Report end date (YYYY-MM-DD)
            
        Returns:
            Occupancy report data or None on error
        """
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        result = self._make_request("GET", "/api/hocc/reports/occupancy", params=params)
        
        if result and result.get("success"):
            return result.get("data")
        return None
    
    def get_revenue_report(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get revenue report
        
        Args:
            start_date: Report start date (YYYY-MM-DD)
            end_date: Report end date (YYYY-MM-DD)
            
        Returns:
            Revenue report data or None on error
        """
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        result = self._make_request("GET", "/api/hocc/reports/revenue", params=params)
        
        if result and result.get("success"):
            return result.get("data")
        return None
    
    # Notifications
    
    def send_booking_confirmation(self, booking_id: str) -> bool:
        """
        Send booking confirmation to guest
        
        Args:
            booking_id: Booking ID
            
        Returns:
            True if successful, False otherwise
        """
        result = self._make_request(
            "POST",
            f"/api/hocc/bookings/{booking_id}/send-confirmation"
        )
        
        if result and result.get("success"):
            logger.info(f"Confirmation sent for booking {booking_id}")
            return True
        return False
    
    # Hotel Profile
    
    def get_hotel_profile(self) -> Optional[Dict]:
        """
        Get hotel profile information
        
        Returns:
            Hotel profile data or None on error
        """
        result = self._make_request("GET", "/api/hocc/profile")
        
        if result and result.get("success"):
            return result.get("data")
        return None
    
    def update_hotel_profile(self, **profile_fields) -> Optional[Dict]:
        """
        Update hotel profile
        
        Args:
            **profile_fields: Fields to update
            
        Returns:
            Updated hotel profile or None on error
        """
        result = self._make_request("PUT", "/api/hocc/profile", data=profile_fields)
        
        if result and result.get("success"):
            logger.info("Hotel profile updated successfully")
            return result.get("data")
        return None


# Singleton instance
_travel_studio_service = None


def get_travel_studio_service() -> TravelStudioService:
    """Get singleton instance of TravelStudioService"""
    global _travel_studio_service
    if _travel_studio_service is None:
        _travel_studio_service = TravelStudioService()
    return _travel_studio_service
