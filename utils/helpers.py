import re
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional, Any, Dict, List, Union
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


def extract_phone_number(text: str) -> Optional[str]:
    """Extract phone number from text"""
    # Pattern for Indian phone numbers
    patterns = [
        r"\+91[-\s]?\d{10}",  # +91 followed by 10 digits
        r"91\d{10}",  # 91 followed by 10 digits
        r"\d{10}",  # 10 digits
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            number = match.group()
            # Clean up
            number = re.sub(r"[-\s]", "", number)
            if not number.startswith("+"):
                if number.startswith("91") and len(number) == 12:
                    number = "+" + number
                elif len(number) == 10:
                    number = "+91" + number
            return number

    return None


def parse_date_from_text(text: str, use_current_year: bool = True) -> Optional[str]:
    """Parse date from natural language text with smart year handling"""

    text_lower = text.lower()

    # Check for common date formats
    date_patterns = [
        (r"(\d{1,2})/(\d{1,2})/(\d{4})", "DD/MM/YYYY"),
        (r"(\d{1,2})-(\d{1,2})-(\d{4})", "DD-MM-YYYY"),
        (r"(\d{1,2})/(\d{1,2})/(\d{2})", "DD/MM/YY"),  # 2-digit year
    ]

    for pattern, format_type in date_patterns:
        match = re.search(pattern, text)
        if match:
            if format_type in ["DD/MM/YYYY", "DD-MM-YYYY"]:
                return f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
            elif format_type == "DD/MM/YY":
                # Convert 2-digit year to 4-digit (assume 20XX)
                year = f"20{match.group(3)}"
                return f"{match.group(1)}/{match.group(2)}/{year}"

    # Check for relative dates
    today = datetime.now()
    current_year = today.year

    if "today" in text_lower:
        return today.strftime("%d/%m/%Y")
    elif "tomorrow" in text_lower:
        tomorrow = today + timedelta(days=1)
        return tomorrow.strftime("%d/%m/%Y")

    # Extract month names (abbreviated or full)
    month_patterns = {
        r"\b(jan|january)\b": 1,
        r"\b(feb|february)\b": 2,
        r"\b(mar|march)\b": 3,
        r"\b(apr|april)\b": 4,
        r"\b(may)\b": 5,
        r"\b(jun|june)\b": 6,
        r"\b(jul|july)\b": 7,
        r"\b(aug|august)\b": 8,
        r"\b(sep|september|sept)\b": 9,
        r"\b(oct|october)\b": 10,
        r"\b(nov|november)\b": 11,
        r"\b(dec|december)\b": 12,
    }

    for pattern, month_num in month_patterns.items():
        month_match = re.search(pattern, text_lower)
        if month_match:
            # Look for day number before or after month
            day_pattern = r"\b(\d{1,2})(st|nd|rd|th)?\b"
            day_matches = re.findall(day_pattern, text_lower)

            if day_matches:
                day = int(day_matches[0][0])

                # Determine year
                if use_current_year:
                    # If month has passed this year, use next year
                    if month_num < today.month or (
                        month_num == today.month and day < today.day
                    ):
                        year = current_year + 1
                    else:
                        year = current_year
                else:
                    year = current_year

                return f"{day:02d}/{month_num:02d}/{year}"

    return None


def extract_number_from_text(text: str, keyword: str) -> Optional[int]:
    """Extract number associated with a keyword"""
    text_lower = text.lower()
    keyword_lower = keyword.lower()

    # Look for patterns like "2 adults", "3 children", etc.
    pattern = rf"(\d+)\s*{keyword_lower}"
    match = re.search(pattern, text_lower)

    if match:
        return int(match.group(1))

    # Also check reverse pattern "adults: 2"
    pattern = rf"{keyword_lower}\s*:?\s*(\d+)"
    match = re.search(pattern, text_lower)

    if match:
        return int(match.group(1))

    return None


def validate_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    # Remove all non-digit characters
    digits = re.sub(r"\D", "", phone)

    # Should have 10-12 digits (10 for local, 12 with country code)
    return len(digits) in [10, 12]


def format_phone_number(phone: str) -> str:
    """Format phone number to E.164 format"""
    # Remove all non-digit characters
    digits = re.sub(r"\D", "", phone)

    # Add country code if missing
    if len(digits) == 10:
        return f"+91{digits}"
    elif len(digits) == 12 and digits.startswith("91"):
        return f"+{digits}"

    return phone


def truncate_text(text: str, max_length: int = 1500) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text

    return text[:max_length] + "..."


def proto_to_dict(obj: Any) -> Any:
    """
    Recursively convert Protocol Buffer objects to native Python types.

    Handles all protobuf types:
    - RepeatedComposite (protobuf arrays of messages) → Python lists
    - RepeatedScalar (protobuf arrays of primitives) → Python lists
    - MapComposite (protobuf maps) → Python dicts
    - Nested protobuf messages → Recursively converted dicts
    - Regular Python types → Pass through unchanged

    This ensures ZERO serialization errors when saving to JSON/database.

    Args:
        obj: Any object (protobuf or native Python type)

    Returns:
        JSON-serializable native Python object
    """
    # Handle None
    if obj is None:
        return None

    # Check if it's a protobuf RepeatedComposite (array of messages)
    type_name = type(obj).__name__

    if "RepeatedComposite" in type_name or "RepeatedScalar" in type_name:
        # Convert protobuf repeated fields to Python list
        return [proto_to_dict(item) for item in obj]

    if "MapComposite" in type_name:
        # Convert protobuf map to Python dict
        return {key: proto_to_dict(value) for key, value in obj.items()}

    # Handle dict (recursively convert values)
    if isinstance(obj, dict):
        return {key: proto_to_dict(value) for key, value in obj.items()}

    # Handle list/tuple (recursively convert items)
    if isinstance(obj, (list, tuple)):
        return [proto_to_dict(item) for item in obj]

    # Handle protobuf Message types (have DESCRIPTOR attribute)
    if hasattr(obj, "DESCRIPTOR") and hasattr(obj, "ListFields"):
        # This is a protobuf message - convert to dict
        result = {}
        for field, value in obj.ListFields():
            result[field.name] = proto_to_dict(value)
        return result

    # Native Python types - pass through
    if isinstance(obj, (str, int, float, bool)):
        return obj

    # Datetime objects
    if isinstance(obj, datetime):
        return obj.isoformat()

    # Decimal objects
    if isinstance(obj, Decimal):
        return float(obj)

    # For anything else, try to convert to string as fallback
    try:
        # If it has __dict__, try that
        if hasattr(obj, "__dict__"):
            return proto_to_dict(obj.__dict__)
        # Otherwise convert to string
        return str(obj)
    except Exception as e:
        logger.warning(f"Could not convert object of type {type(obj)}: {e}")
        return str(obj)


def safe_json_serialize(obj: Any, fallback_repr: bool = True) -> Any:
    """
    Safely serialize ANY object to JSON-compatible format.

    This is a bulletproof serializer that handles:
    - All native Python types (dict, list, str, int, float, bool, None)
    - datetime objects → ISO format strings
    - Decimal, UUID → Strings
    - Protocol Buffer objects → Converted via proto_to_dict()
    - Custom objects → Use __dict__ or str() as fallback
    - Circular references → Detected and handled

    Args:
        obj: Any object to serialize
        fallback_repr: If True, use string representation for unknown types

    Returns:
        JSON-serializable object
    """
    # Keep track of seen objects to detect circular references
    seen = set()

    def _serialize(o: Any, depth: int = 0) -> Any:
        # Prevent infinite recursion
        if depth > 50:
            return "<max_depth_reached>"

        # Handle None
        if o is None:
            return None

        # Handle basic JSON-serializable types
        if isinstance(o, (str, int, float, bool)):
            return o

        # Handle datetime
        if isinstance(o, datetime):
            return o.isoformat()

        # Handle Decimal
        if isinstance(o, Decimal):
            return float(o)

        # Handle bytes
        if isinstance(o, bytes):
            try:
                return o.decode("utf-8")
            except:
                return str(o)

        # Check for circular reference (using id())
        obj_id = id(o)
        if obj_id in seen:
            return "<circular_reference>"

        # Handle Protocol Buffer objects first
        type_name = type(o).__name__
        if (
            "RepeatedComposite" in type_name
            or "RepeatedScalar" in type_name
            or "MapComposite" in type_name
        ):
            return proto_to_dict(o)

        if hasattr(o, "DESCRIPTOR") and hasattr(o, "ListFields"):
            return proto_to_dict(o)

        # Handle dict
        if isinstance(o, dict):
            seen.add(obj_id)
            try:
                result = {str(k): _serialize(v, depth + 1) for k, v in o.items()}
            finally:
                seen.discard(obj_id)
            return result

        # Handle list/tuple
        if isinstance(o, (list, tuple)):
            seen.add(obj_id)
            try:
                result = [_serialize(item, depth + 1) for item in o]
            finally:
                seen.discard(obj_id)
            return result

        # Handle set
        if isinstance(o, set):
            return list(o)

        # Try JSON serialization first
        try:
            json.dumps(o)
            return o
        except (TypeError, ValueError):
            pass

        # Fallback: Try __dict__
        if hasattr(o, "__dict__"):
            seen.add(obj_id)
            try:
                result = {
                    str(k): _serialize(v, depth + 1)
                    for k, v in o.__dict__.items()
                    if not k.startswith("_")
                }
            finally:
                seen.discard(obj_id)
            return result

        # Final fallback: string representation
        if fallback_repr:
            return str(o)

        return None

    try:
        return _serialize(obj)
    except Exception as e:
        logger.error(f"Serialization error: {e}")
        return {"error": "serialization_failed", "type": str(type(obj))}


def sanitize_tool_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize tool parameters to ensure they are JSON-serializable.

    This function:
    - Converts protobuf objects to native Python types
    - Validates and converts data types
    - Removes None values from optional fields
    - Ensures all values are JSON-serializable

    Args:
        params: Dictionary of tool parameters

    Returns:
        Sanitized parameters dictionary
    """
    # First convert any protobuf objects
    sanitized = proto_to_dict(params)

    # Then apply safe serialization
    sanitized = safe_json_serialize(sanitized)

    # Remove None values (optional fields)
    if isinstance(sanitized, dict):
        sanitized = {k: v for k, v in sanitized.items() if v is not None}

    return sanitized


def send_email(
    to_email: str,
    subject: str,
    body: str,
    is_html: bool = False,
    from_email: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Send email via SMTP.

    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body (can be plain text or HTML)
        is_html: Whether body is HTML (default: False)
        from_email: Sender email (uses SMTP_FROM_EMAIL env var if not provided)

    Returns:
        Dictionary with success status and message
    """
    try:
        # Get email configuration from environment
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        from_email = from_email or os.getenv(
            "SMTP_FROM_EMAIL", "noreply@singhanahaveli.com"
        )

        # Validate configuration
        if not all([smtp_server, smtp_user, smtp_password]):
            logger.error(
                "Email configuration incomplete: SMTP_SERVER, SMTP_USER, or SMTP_PASSWORD not set"
            )
            return {"success": False, "error": "Email service not configured"}

        # Create email message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email

        # Attach body
        if is_html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        logger.info(f"Email sent successfully to {to_email}")
        return {"success": True, "message": f"Email sent to {to_email}"}

    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed - check SMTP_USER and SMTP_PASSWORD")
        return {"success": False, "error": "SMTP authentication failed"}

    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {str(e)}")
        return {"success": False, "error": f"SMTP error: {str(e)}"}

    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return {"success": False, "error": f"Failed to send email: {str(e)}"}
