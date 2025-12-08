"""
WhatsApp Service using AiSensy API
Replaces Twilio with AiSensy for WhatsApp messaging
"""

import os
import logging
import requests
from typing import Dict, Optional
from twilio.rest import Client

logger = logging.getLogger(__name__)


class WhatsAppService:
    def __init__(self):
        """Initialize AiSensy WhatsApp service"""
        self.aisensy_project_id = os.getenv("AISENSY_PROJECT_ID")
        self.aisensy_api_pwd = os.getenv("AISENSY_PROJECT_API_PWD")
        self.whatsapp_phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.whatsapp_access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.whatsapp_api_version = os.getenv("WHATSAPP_API_VERSION", "v24.0")
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        # AiSensy API endpoints
        self.aisensy_base_url = f"https://apis.aisensy.com/project-apis/v1/project/{self.aisensy_project_id}"
        self.aisensy_messages_url = f"{self.aisensy_base_url}/messages"

        # Twilio API endpoints
        self.twilio_client = Client(self.twilio_account_sid,self.twilio_auth_token)
        
        # WhatsApp Business API endpoints (for typing indicator)
        self.whatsapp_base_url = f"https://graph.facebook.com/{self.whatsapp_api_version}/{self.whatsapp_phone_number_id}"
        self.whatsapp_message_url = f"{self.whatsapp_base_url}/messages"
        
        # Validate credentials
        if not self.aisensy_project_id or not self.aisensy_api_pwd or not self.whatsapp_phone_number_id or not self.whatsapp_access_token:
            logger.warning("credentials not found. WhatsApp sending disabled.")
            self.client_initialized = False
        else:
            self.client_initialized = True
            logger.info("AiSensy WhatsApp service initialized")
    
    
    def sanitize_phone(self, phone: str) -> str:
        """
        Sanitize phone number to format required by AiSensy
        Expected format: 919999999999 (country code + number, no spaces, no +)
        """
        if not phone:
            return phone
        
        # Remove whatsapp: prefix if present (from Twilio format)
        phone = phone.replace("whatsapp:", "")
        
        phone = phone.strip()
        # Remove all non-digit characters
        phone = ''.join(ch for ch in phone if ch.isdigit())
        
        # If starts with 0, remove it
        if phone.startswith("0"):
            phone = phone.lstrip("0")
        
        # If 10 digits, assume India and add 91
        if len(phone) == 10:
            return f"91{phone}"
        
        # If already has country code (starts with 91 and has 12 digits), return as is
        if phone.startswith("91") and len(phone) == 12:
            return phone
        
        return phone
    
    
    def send_message(self, to_number: str, message: str) -> bool:
        """
        Send WhatsApp message via AiSensy API
        
        Args:
            to_number: Recipient phone number
            message: Message text to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.client_initialized:
                logger.error("AiSensy client not initialized")
                return False
            
            # Sanitize phone number
            to_number = self.sanitize_phone(to_number)
            
            if not to_number:
                logger.error("Invalid phone number after sanitization")
                return False
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-AiSensy-Project-API-Pwd": self.aisensy_api_pwd
            }
            
            payload = {
                "to": to_number,
                "type": "text",
                "recipient_type": "individual",
                "text": {
                    "body": message
                }
            }
            
            logger.info(f"Sending WhatsApp message to {to_number}")
            
            response = requests.post(
                self.aisensy_messages_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract message ID from AiSensy response
            messages = result.get("messages", [])
            message_id = messages[0].get("id", "") if messages else ""
            message_status = messages[0].get("message_status", "") if messages else ""
            
            logger.info(f"Message sent successfully to {to_number}")
            logger.info(f"Message ID: {message_id}, Status: {message_status}")
            
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message: {str(e)}")
            return False
    

        
    def send_message_using_WABA(self, to_number: str, message: str) -> bool:
        """
        Send WhatsApp message via WABA API
        
        Args:
            to_number: Recipient phone number
            message: Message text to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.client_initialized:
                logger.error("client not initialized")
                return False
            
            # Sanitize phone number
            to_number = self.sanitize_phone(to_number)
            
            if not to_number:
                logger.error("Invalid phone number after sanitization")
                return False
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.whatsapp_access_token}"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            logger.info(f"Sending WhatsApp message to {to_number}")
            
            response = requests.post(
                self.whatsapp_message_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract message ID from AiSensy response
            messages = result.get("messages", [])
            message_id = messages[0].get("id", "") if messages else ""
            message_status = messages[0].get("message_status", "") if messages else ""
            
            logger.info(f"Message sent successfully to {to_number}")
            logger.info(f"Message ID: {message_id}, Status: {message_status}")
            
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message: {str(e)}")
            return False
    

            
    def send_message_using_Twilio(self, to_number: str, message: str) -> bool:
        """
        Send WhatsApp message via Twilio
        
        Args:
            to_number: Recipient phone number
            message: Message text to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.client_initialized:
                logger.error("client not initialized")
                return False
            
            # Sanitize phone number
            to_number = self.sanitize_phone(to_number)
            
            if not to_number:
                logger.error("Invalid phone number after sanitization")
                return False
            
            logger.info(f"Sending WhatsApp message to {to_number}")
            
            response = self.twilio_client.messages.create(
                from_=f"whatsapp:{self.twilio_phone_number}",
                to=f"whatsapp:+{to_number}",
                body=message
            )
            
            logger.info(f"Message sent successfully to {to_number}")
            logger.info(f"Message Body: {response.body}")
            
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message: {str(e)}")
            return False
    


    
    def send_typing_indicator(self, to_number: str, message_id: Optional[str] = None) -> bool:
        """
        Send typing indicator / mark message as read via WhatsApp Business API
        
        Args:
            to_number: Recipient phone number
            message_id: Message ID to mark as read
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.whatsapp_phone_number_id or not self.whatsapp_access_token:
                logger.warning("WhatsApp Business API credentials not configured")
                return False
            
            url = f"{self.whatsapp_base_url}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.whatsapp_access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "typing_indicator": {
                    "type": "text"
                }
            }
            
            if message_id:
                payload["message_id"] = message_id
            
            response = requests.post(url, headers=headers, json=payload, timeout=5)
            response.raise_for_status()
            
            logger.info(f"Typing indicator sent for {to_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending typing indicator: {str(e)}")
            return False
    
    
    def parse_incoming_message(self, data: dict) -> Dict[str, str]:
        """
        Parse incoming WhatsApp webhook data from WhatsApp Business API
        
        Supports both WhatsApp Business API format and Twilio format for compatibility
        
        Args:
            data: Webhook data dictionary
            
        Returns:
            dict: Parsed message data with standardized keys
        """
        try:
            # Try WhatsApp Business API format first (AiSensy webhook)
            if "data" in data and "message" in data.get("data", {}):
                message_data = data["data"]["message"]
                
                # Extract message content
                message_content = message_data.get("message_content", {})
                body = ""
                
                if isinstance(message_content, dict):
                    # Text message
                    if "text" in message_content:
                        body = message_content["text"]
                    # Could also be image, audio, video, etc.
                    elif "caption" in message_content:
                        body = message_content["caption"]
                
                return {
                    "message_sid": message_data.get("messageId", ""),
                    "from_number": message_data.get("phone_number", ""),
                    "to_number": self.whatsapp_phone_number_id or "",
                    "body": body,
                    "num_media": 0,  # Would need to check message_content type
                    "profile_name": message_data.get("userName", ""),
                    "timestamp": message_data.get("timestamp", ""),
                    "message_type": message_data.get("type", "text")
                }
            
            # Fallback to Twilio format for compatibility
            elif "MessageSid" in data or "From" in data:
                return {
                    "message_sid": data.get("MessageSid", ""),
                    "from_number": data.get("From", "").replace("whatsapp:", ""),
                    "to_number": data.get("To", "").replace("whatsapp:", ""),
                    "body": data.get("Body", ""),
                    "num_media": int(data.get("NumMedia", 0)),
                    "profile_name": data.get("ProfileName", ""),
                    "timestamp": "",
                    "message_type": "text"
                }
            
            else:
                logger.error("Unknown webhook format")
                return {
                    "message_sid": "",
                    "from_number": "",
                    "to_number": "",
                    "body": "",
                    "num_media": 0,
                    "profile_name": "",
                    "timestamp": "",
                    "message_type": "unknown"
                }
                
        except Exception as e:
            logger.error(f"Error parsing incoming message: {str(e)}")
            return {
                "message_sid": "",
                "from_number": "",
                "to_number": "",
                "body": "",
                "num_media": 0,
                "profile_name": "",
                "timestamp": "",
                "message_type": "error"
            }
    
    
    def create_response(self, message: str) -> str:
        """
        Create webhook response
        For WhatsApp Business API, we just return success status
        Messages are sent via the send_message method instead
        
        Args:
            message: Message to send (not used with WhatsApp Business API)
            
        Returns:
            str: Empty string or success JSON
        """
        # WhatsApp Business API doesn't use TwiML responses
        # Messages are sent separately via the API
        return '{"status": "success"}'