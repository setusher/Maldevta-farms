import httpx
import os
from typing import Dict, Any
import logging
from datetime import datetime
from utils.helpers import sanitize_tool_params
from services.travel_studio_service import get_travel_studio_service

logger = logging.getLogger(__name__)


class ToolService:
    def __init__(self):
        self.base_url = os.getenv(
            "TOOLS_API_BASE_URL", "https://singhanahaveliagent.vercel.app"
        )
        self.api_token = os.getenv("TOOLS_API_TOKEN")
        self.client = httpx.AsyncClient(timeout=30.0)
        self.travel_studio = get_travel_studio_service()

    def _sanitize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize parameters to ensure they are JSON-serializable.
        Handles protobuf objects, type conversions, and validation.
        """
        try:
            # Use the universal sanitizer from helpers
            sanitized = sanitize_tool_params(params)

            # Additional type conversions for common cases
            if isinstance(sanitized, dict):
                for key, value in sanitized.items():
                    # Convert floats to ints for fields that should be integers
                    if key in [
                        "num_of_adults",
                        "num_of_children",
                        "num_of_rooms",
                        "extra_guest",
                        "age",
                        "num_of_people",
                    ] and isinstance(value, float):
                        sanitized[key] = int(value)

                    # Ensure strings are properly formatted
                    elif isinstance(value, str):
                        sanitized[key] = value.strip()

            return sanitized

        except Exception as e:
            logger.error(f"Error sanitizing params: {e}")
            # Return params as-is if sanitization fails
            return params

    async def call_tool(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call external tool API with sanitized parameters"""
        try:
            # CRITICAL: Sanitize parameters to prevent serialization errors
            safe_params = self._sanitize_params(parameters)

            url = f"{self.base_url}/{tool_name}"
            headers = {"Content-Type": "application/json"}

            # Add token if provided
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"

            logger.info(
                f"Calling tool: {tool_name} with sanitized params: {safe_params}"
            )

            response = await self.client.post(url, json=safe_params, headers=headers)
            response.raise_for_status()
            result = response.json()

            logger.info(f"Tool {tool_name} response: {result}")
            return result

        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling {tool_name}: {str(e)}")
            return {"success": False, "error": f"Failed to call {tool_name}: {str(e)}"}
        except Exception as e:
            logger.error(f"Error calling {tool_name}: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def check_availability(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check availability using Travel Studio API - converts DD/MM/YYYY to YYYY-MM-DD format"""
        # Sanitize params first
        params = self._sanitize_params(params)

        # Convert date format for API
        check_in = params.get("check_in")
        check_out = params.get("check_out")
        
        if check_in:
            try:
                # Parse DD/MM/YYYY and convert to YYYY-MM-DD
                check_in_date = datetime.strptime(str(check_in), "%d/%m/%Y")
                check_in = check_in_date.strftime("%Y-%m-%d")
            except Exception as e:
                logger.warning(
                    f"Date conversion failed for check_in: {check_in}, error: {e}"
                )

        if check_out:
            try:
                check_out_date = datetime.strptime(str(check_out), "%d/%m/%Y")
                check_out = check_out_date.strftime("%Y-%m-%d")
            except Exception as e:
                logger.warning(
                    f"Date conversion failed for check_out: {check_out}, error: {e}"
                )

        # Use Travel Studio API to check availability
        try:
            logger.info(f"Checking availability via Travel Studio API: {check_in} to {check_out}")
            
            available_rooms = self.travel_studio.get_available_rooms(
                check_in_date=check_in,
                check_out_date=check_out,
                room_type=params.get("room_type_id"),
                num_adults=params.get("num_of_adults"),
                num_children=params.get("num_of_children")
            )
            
            if available_rooms is not None:
                # Format response to match expected structure
                num_rooms_requested = params.get("num_of_rooms", 1)
                budget = params.get("budget")
                
                # Filter by budget if specified
                if budget:
                    available_rooms = [
                        room for room in available_rooms 
                        if room.get("base_rate", 0) <= budget
                    ]
                
                # Group by category and calculate availability
                room_summary = {}
                for room in available_rooms:
                    category = room.get("category", "Unknown")
                    if category not in room_summary:
                        room_summary[category] = {
                            "category": category,
                            "available_count": 0,
                            "base_rate": room.get("base_rate", 0),
                            "rooms": []
                        }
                    room_summary[category]["available_count"] += 1
                    room_summary[category]["rooms"].append(room)
                
                return {
                    "success": True,
                    "data": {
                        "available_rooms": list(room_summary.values()),
                        "total_available": len(available_rooms),
                        "check_in": check_in,
                        "check_out": check_out,
                        "num_of_adults": params.get("num_of_adults"),
                        "num_of_children": params.get("num_of_children"),
                        "num_of_rooms": num_rooms_requested
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to fetch room availability from Travel Studio API"
                }
                
        except Exception as e:
            logger.error(f"Error checking availability: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to check availability: {str(e)}"
            }

    async def create_booking_reservation(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create booking using Travel Studio API - converts DD/MM/YYYY to YYYY-MM-DD format"""
        # Sanitize params first (CRITICAL FIX for protobuf arrays)
        params = self._sanitize_params(params)

        # Convert date format for API
        check_in = params.get("check_in")
        check_out = params.get("check_out")
        
        if check_in:
            try:
                check_in_date = datetime.strptime(str(check_in), "%d/%m/%Y")
                check_in = check_in_date.strftime("%Y-%m-%d")
            except Exception as e:
                logger.warning(
                    f"Date conversion failed for check_in: {check_in}, error: {e}"
                )

        if check_out:
            try:
                check_out_date = datetime.strptime(str(check_out), "%d/%m/%Y")
                check_out = check_out_date.strftime("%Y-%m-%d")
            except Exception as e:
                logger.warning(
                    f"Date conversion failed for check_out: {check_out}, error: {e}"
                )

        # Use Travel Studio API to create booking
        try:
            logger.info(f"Creating booking via Travel Studio API: {params.get('name')}")
            
            # Determine room type from room_type_ids array
            room_type = "Deluxe"  # Default
            if params.get("room_type_ids") and len(params["room_type_ids"]) > 0:
                room_type = params["room_type_ids"][0]
            
            booking = self.travel_studio.create_booking(
                guest_name=params.get("name", ""),
                guest_email=params.get("email", "guest@example.com"),
                guest_phone=params.get("phone_number", ""),
                check_in_date=check_in,
                check_out_date=check_out,
                room_type=room_type,
                number_of_guests=params.get("num_of_adults", 1) + params.get("num_of_children", 0),
                special_requests=params.get("special_request", "")
            )
            
            if booking:
                logger.info(f"Booking created successfully via Travel Studio")
                return {
                    "success": True,
                    "data": booking,
                    "message": "Booking created successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create booking via Travel Studio API"
                }
                
        except Exception as e:
            logger.error(f"Error creating booking: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to create booking: {str(e)}"
            }

    async def create_day_outing_reservation(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create day outing - converts DD/MM/YYYY to YYYY-MM-DD format"""
        # Sanitize params first
        params = self._sanitize_params(params)

        # Convert date format for API
        if "preferred_date" in params and params["preferred_date"]:
            try:
                date = datetime.strptime(str(params["preferred_date"]), "%d/%m/%Y")
                params["preferred_date"] = date.strftime("%Y-%m-%d")
            except Exception as e:
                logger.warning(
                    f"Date conversion failed for preferred_date: {params['preferred_date']}, error: {e}"
                )

        # Also handle 'date' field if present
        if "date" in params and params["date"]:
            try:
                date = datetime.strptime(str(params["date"]), "%d/%m/%Y")
                params["date"] = date.strftime("%Y-%m-%d")
            except Exception as e:
                logger.warning(
                    f"Date conversion failed for date: {params['date']}, error: {e}"
                )

        return await self.call_tool("create_day_outing_reservation", params)

    async def create_event_inquiry(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create event inquiry - sends email to owner"""
        params = self._sanitize_params(params)
        
        # Handle date fields
        for date_field in ["starting_date", "end_date"]:
            if date_field in params and params[date_field]:
                try:
                    date = datetime.strptime(str(params[date_field]), "%d/%m/%Y")
                    params[date_field] = date.strftime("%Y-%m-%d")
                except Exception as e:
                    logger.warning(
                        f"Date conversion failed for {date_field}: {params[date_field]}, error: {e}"
                    )
        
        # Send email to owner about event inquiry
        try:
            logger.info(f"Creating event inquiry for {params.get('name')}")
            
            subject = f"Event Inquiry - {params.get('purpose', 'Event')} - {params.get('name')}"
            
            body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #f8f9fa; border-left: 4px solid #007bff; padding: 20px; margin-bottom: 20px;">
                    <h2 style="margin: 0 0 10px 0; color: #007bff;">New Event Inquiry</h2>
                    <p style="margin: 0; color: #666;">WhatsApp Booking Agent</p>
                </div>
                
                <div style="background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 5px; padding: 20px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #007bff; border-bottom: 2px solid #007bff; padding-bottom: 10px;">Guest Details</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold; width: 150px;">Name:</td>
                            <td style="padding: 8px 0;">{params.get('name', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Phone:</td>
                            <td style="padding: 8px 0;">{params.get('phone_number', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Age:</td>
                            <td style="padding: 8px 0;">{params.get('age', 'N/A')}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 5px; padding: 20px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #007bff; border-bottom: 2px solid #007bff; padding-bottom: 10px;">Event Details</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold; width: 150px;">Purpose:</td>
                            <td style="padding: 8px 0;">{params.get('purpose', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Starting Date:</td>
                            <td style="padding: 8px 0;">{params.get('starting_date', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold;">End Date:</td>
                            <td style="padding: 8px 0;">{params.get('end_date', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Number of People:</td>
                            <td style="padding: 8px 0;">{params.get('num_of_people', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Special Requests:</td>
                            <td style="padding: 8px 0;">{params.get('special_request', 'None')}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background-color: #d1ecf1; border-left: 4px solid #17a2b8; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #0c5460;">
                        <strong>⚠️ Action Required:</strong> Please contact the customer at <strong>{params.get('phone_number', 'N/A')}</strong> to discuss event details and provide a quote.
                    </p>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                    <p style="margin: 0; color: #999; font-size: 12px; font-style: italic;">
                        This is an automated inquiry from the WhatsApp booking agent.
                    </p>
                </div>
            </body>
            </html>
            """
            
            email_params = {
                "to_email": os.getenv("OWNER_EMAIL"),
                "subject": subject,
                "body": body,
            }
            
            result = await self.call_tool("send_email", email_params)
            
            if result.get("success"):
                logger.info(f"Event inquiry email sent successfully")
                return {
                    "success": True,
                    "message": "Event inquiry submitted successfully. Our team will contact you within 24 hours."
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error creating event inquiry: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to create event inquiry: {str(e)}"
            }

    async def lead_gen(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate lead - sends email to owner"""
        params = self._sanitize_params(params)
        
        try:
            logger.info(f"Generating lead for {params.get('name')}")
            
            lead_type = params.get('type_of_lead', 'GENERAL')
            subject = f"New Lead - {lead_type} - {params.get('name')}"
            
            body = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #f8f9fa; border-left: 4px solid #28a745; padding: 20px; margin-bottom: 20px;">
                    <h2 style="margin: 0 0 10px 0; color: #28a745;">New Lead Generated</h2>
                    <p style="margin: 0; color: #666;">WhatsApp Booking Agent</p>
                </div>
                
                <div style="background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 5px; padding: 20px;">
                    <h3 style="margin-top: 0; color: #28a745;">Lead Details</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold; width: 150px;">Name:</td>
                            <td style="padding: 8px 0;">{params.get('name', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Phone:</td>
                            <td style="padding: 8px 0;">{params.get('phone_number', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Type:</td>
                            <td style="padding: 8px 0;">{lead_type}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background-color: #d1ecf1; border-left: 4px solid #17a2b8; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #0c5460;">
                        <strong>Follow up:</strong> Contact {params.get('name')} at {params.get('phone_number')} for {lead_type}.
                    </p>
                </div>
            </body>
            </html>
            """
            
            email_params = {
                "to_email": os.getenv("OWNER_EMAIL"),
                "subject": subject,
                "body": body,
            }
            
            result = await self.call_tool("send_email", email_params)
            
            if result.get("success"):
                logger.info(f"Lead generation email sent successfully")
                return {
                    "success": True,
                    "message": "Lead captured successfully. Our team will follow up soon."
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error generating lead: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to generate lead: {str(e)}"
            }

    async def human_followup(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule human followup - sends email to owner"""
        params = self._sanitize_params(params)
        
        try:
            logger.info(f"Scheduling human followup for {params.get('name')}")
            
            subject = f"Follow-up Request - {params.get('name')}"
            
            body = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; margin-bottom: 20px;">
                    <h2 style="margin: 0 0 10px 0; color: #856404;">Follow-up Request</h2>
                    <p style="margin: 0; color: #666;">WhatsApp Booking Agent</p>
                </div>
                
                <div style="background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 5px; padding: 20px;">
                    <h3 style="margin-top: 0; color: #856404;">Customer Details</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold; width: 150px;">Name:</td>
                            <td style="padding: 8px 0;">{params.get('name', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Phone:</td>
                            <td style="padding: 8px 0;">{params.get('phone_number', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Purpose:</td>
                            <td style="padding: 8px 0;">{params.get('purpose', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Requested Time:</td>
                            <td style="padding: 8px 0;">{params.get('schedule_time', 'ASAP')}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #721c24;">
                        <strong>⚠️ Action Required:</strong> Please call {params.get('name')} at {params.get('phone_number')} at the scheduled time.
                    </p>
                </div>
            </body>
            </html>
            """
            
            email_params = {
                "to_email": os.getenv("OWNER_EMAIL"),
                "subject": subject,
                "body": body,
            }
            
            result = await self.call_tool("send_email", email_params)
            
            if result.get("success"):
                logger.info(f"Follow-up request email sent successfully")
                return {
                    "success": True,
                    "message": "Follow-up scheduled successfully. Our team will call you at the requested time."
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error scheduling followup: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to schedule followup: {str(e)}"
            }

    async def confirm_payment_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params = self._sanitize_params(params)
        return await self.call_tool("confirm_payment_details", params)

    async def general_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return general hotel information - hardcoded for Maldevta Farms"""
        logger.info("Fetching general hotel information")
        
        return {
            "success": True,
            "data": {
                "name": "Maldevta Farms",
                "location": "Maldevta, Dehradun, Uttarakhand",
                "description": "A peaceful riverside nature resort with pinewood cottages, hill views, open lawns, and outdoor learning experiences",
                "contact": {
                    "phone": "+1 (774) 445-1439",
                    "email": "info@maldevtafarms.com"
                },
                "amenities": [
                    "Riverside location",
                    "Pinewood cottages",
                    "Hill views",
                    "Open lawns",
                    "Outdoor experiences",
                    "Nature trails",
                    "Breakfast included"
                ],
                "check_in_time": "2:00 PM",
                "check_out_time": "11:00 AM",
                "distance_from_city": "~17 km from Dehradun city center",
                "distance_from_airport": "<20 km from airport",
                "room_types": ["Deluxe", "Luxury Cottage", "Basic"],
                "policies": [
                    "Breakfast is complimentary with all bookings",
                    "Full payment required at booking",
                    "Cancellation requests handled via team contact",
                    "Events and large groups require special arrangements"
                ]
            },
            "message": "General information retrieved successfully"
        }

    async def get_all_room_reservations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get all room reservations using Travel Studio API"""
        try:
            logger.info("Fetching all room reservations via Travel Studio API")
            
            bookings = self.travel_studio.get_bookings()
            
            if bookings is not None:
                return {
                    "success": True,
                    "data": {
                        "bookings": bookings,
                        "count": len(bookings)
                    },
                    "message": f"Found {len(bookings)} bookings"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to fetch bookings from Travel Studio API"
                }
                
        except Exception as e:
            logger.error(f"Error fetching bookings: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to fetch bookings: {str(e)}"
            }

    async def get_all_day_outing_reservations(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        params = self._sanitize_params(params)
        return await self.call_tool("get_all_day_outing_reservations", params)

    async def get_all_event_inquiries(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params = self._sanitize_params(params)
        return await self.call_tool("get_all_event_inquiries", params)

    # DISABLED: Maldevta Farms does not offer hourly bookings
    # async def check_hourly_availability(self, params: Dict[str, Any]) -> Dict[str, Any]:
    #     """Check hourly availability - NOT AVAILABLE FOR MALDEVTA"""
    #     return {
    #         "success": False,
    #         "error": "Hourly bookings are not available at Maldevta Farms. We offer full-day stays only."
    #     }
    
    # async def create_hourly_booking_reservation(self, params: Dict[str, Any]) -> Dict[str, Any]:
    #     """Create hourly booking - NOT AVAILABLE FOR MALDEVTA"""
    #     return {
    #         "success": False,
    #         "error": "Hourly bookings are not available at Maldevta Farms. We offer full-day stays only."
    #     }
    
    # async def get_hourly_booking_by_id(self, params: Dict[str, Any]) -> Dict[str, Any]:
    #     """Get hourly booking - NOT AVAILABLE FOR MALDEVTA"""
    #     return {
    #         "success": False,
    #         "error": "Hourly bookings are not available at Maldevta Farms."
    #     }

    async def location_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send location info via WhatsApp template"""
        params = self._sanitize_params(params)
        return await self.call_tool("location_info", params)

    async def request_update_or_cancel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cancellation or update requests - sends email to owner via /send_email endpoint"""
        params = self._sanitize_params(params)
        
        # Extract parameters
        customer_name = params.get("customer_name", "")
        customer_phone = params.get("customer_phone", "")
        booking_type = params.get("booking_type", "")
        request_type = params.get("request_type", "")
        request_details = params.get("request_details", "")
        
        # Build friendly booking type name
        booking_type_friendly = {
            "full-day": "Full-Day Room Booking",
            "hourly-booking": "Hourly Room Booking",
            "day-outing": "Day Outing",
            "enquiry": "Event Enquiry",
        }.get(booking_type, booking_type.title())
        
        # Build email content
        action_text = "CANCEL" if request_type.lower() == "cancel" else "UPDATE"
        subject = f"[{action_text}] {booking_type_friendly} Request - {customer_name}"
        
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; border-left: 4px solid #28a745; padding: 20px; margin-bottom: 20px;">
                <h2 style="margin: 0 0 10px 0; color: #28a745;">Booking {action_text} Request</h2>
                <p style="margin: 0; color: #666;">WhatsApp Booking Agent</p>
            </div>
            
            <p>Dear Team,</p>
            <p>A new booking {action_text.lower()} request has been received via WhatsApp:</p>
            
            <div style="background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 5px; padding: 20px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #28a745; border-bottom: 2px solid #28a745; padding-bottom: 10px;">Customer Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold; width: 130px;">Name:</td>
                        <td style="padding: 8px 0;">{customer_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">Phone:</td>
                        <td style="padding: 8px 0;">{customer_phone}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">Booking Type:</td>
                        <td style="padding: 8px 0;">{booking_type_friendly}</td>
                    </tr>
                </table>
            </div>
            
            <div style="background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 5px; padding: 15px; margin: 20px 0;">
                <p style="margin: 0; font-weight: bold; color: #856404;">Request Type: {request_type.upper()}</p>
            </div>
            
            <div style="background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 5px; padding: 20px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #28a745; border-bottom: 2px solid #28a745; padding-bottom: 10px;">Request Details</h3>
                <p style="margin: 0; white-space: pre-wrap;">{request_details}</p>
            </div>
            
            <div style="background-color: #d1ecf1; border-left: 4px solid #17a2b8; padding: 15px; margin: 20px 0;">
                <p style="margin: 0; color: #0c5460;">
                    <strong>⚠️ Action Required:</strong> Please contact the customer at <strong>{customer_phone}</strong> to process this request.
                </p>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                <p style="margin: 0; color: #999; font-size: 12px; font-style: italic;">
                    This is an automated request from the WhatsApp booking agent.
                </p>
            </div>
        </body>
        </html>
        """
                # Call existing /send_email endpoint instead
                
        email_params = {
            "to_email": os.getenv("OWNER_EMAIL"),
            "subject": subject,
            "body": body,
        }
        
        return await self.call_tool("send_email", email_params)

    async def close(self):
        await self.client.aclose()
