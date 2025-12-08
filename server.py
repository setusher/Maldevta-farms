"""
Vercel-Optimized WhatsApp Server with Upstash QStash
Updated to use AiSensy API instead of Twilio
No timeout errors, optimized for Vercel deployment
"""

from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import Response, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import logging
import os
import httpx
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from database import init_db, get_db
from services import WhatsAppService
from services import AgentService
from services import get_travel_studio_service

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting WhatsApp Agent Server (AiSensy + QStash Mode)...")
    init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down...")


# Initialize FastAPI
app = FastAPI(
    title="WhatsApp Reservation Agent",
    description="AI-powered WhatsApp agent with AiSensy API and QStash background processing",
    version="3.0.0",
    lifespan=lifespan,
)

# QStash configuration
QSTASH_URL = os.getenv("QSTASH_URL", "https://qstash.upstash.io")
QSTASH_TOKEN = os.getenv("QSTASH_TOKEN")
BASE_URL = os.getenv("BASE_URL", "https://whatsapp.gydexp.in")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "WhatsApp Reservation Agent",
        "provider": "AiSensy + WhatsApp Business API",
        "mode": "qstash-async",
        "version": "3.0.0",
    }


@app.get("/health")
async def health_check():
    """Health check for monitoring"""
    aisensy_configured = bool(
        os.getenv("AISENSY_PROJECT_ID") and os.getenv("AISENSY_PROJECT_API_PWD")
    )
    qstash_configured = bool(QSTASH_TOKEN)

    return {
        "status": "healthy",
        "aisensy_configured": aisensy_configured,
        "qstash_configured": qstash_configured,
        "base_url": BASE_URL,
    }


@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    """
    FAST webhook endpoint - responds in <1 second
    Queues message to QStash for async processing

    Supports both:
    - WhatsApp Business API webhook format (AiSensy)
    - Twilio webhook format (for backward compatibility)

    NO TIMEOUT ERRORS! ✅
    """
    try:
        # Try to parse as JSON first (WhatsApp Business API / AiSensy)
        content_type = request.headers.get("content-type", "")

        if "application/json" in content_type:
            # WhatsApp Business API format
            json_data = await request.json()
            logger.info(f"Received JSON webhook: {json_data}")

            whatsapp_service = WhatsAppService()
            parsed = whatsapp_service.parse_incoming_message(json_data)

        else:
            # Twilio form data format (fallback)
            form_data = await request.form()
            form_dict = dict(form_data)
            logger.info(f"Received form webhook: {form_dict}")

            whatsapp_service = WhatsAppService()
            parsed = whatsapp_service.parse_incoming_message(form_dict)

        phone_number = parsed["from_number"]
        user_message = parsed["body"]
        message_sid = parsed["message_sid"]
        user_name = parsed.get("profile_name", "")

        if not user_message:
            logger.info("Empty message received, ignoring")
            return JSONResponse(content={"status": "success"}, status_code=200)

        logger.info(f"📱 Message from {phone_number}: {user_message[:50]}...")
        logger.info(f"👤 User: {user_name}")

        # Send typing indicator immediately (non-blocking)
        # try:
        #     whatsapp_service.send_typing_indicator(phone_number, message_sid)
        # except:
        #     pass  # Don't fail if typing indicator fails

        # Queue to QStash for async processing
        if QSTASH_TOKEN:
            logger.info(f"📤 Queueing to QStash for background processing")

            process_url = f"{BASE_URL}/process-async"

            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    # QStash publishes to destination URL
                    qstash_response = await client.post(
                        f"{QSTASH_URL}/v2/publish/{process_url}",
                        headers={
                            "Authorization": f"Bearer {QSTASH_TOKEN}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "phone": phone_number,
                            "message": user_message,
                            "message_sid": message_sid,
                            "user_name": user_name,
                        },
                    )

                    if qstash_response.status_code in [200, 201, 202]:
                        qstash_data = qstash_response.json()
                        message_id = qstash_data.get("messageId", "unknown")
                        logger.info(
                            f"✅ Message queued successfully! QStash MessageID: {message_id}"
                        )
                    else:
                        logger.error(f"❌ QStash error: {qstash_response.status_code}")

            except Exception as e:
                logger.error(f"Failed to queue to QStash: {str(e)}")
                # Continue anyway - webhook still succeeds
        else:
            logger.warning("⚠️  QStash not configured, processing inline (may timeout)")
            # Process inline if QStash not available (not recommended for production)

        # Return success immediately
        return JSONResponse(content={"status": "success"}, status_code=200)

    except Exception as e:
        logger.error(f"Error in webhook: {str(e)}", exc_info=True)
        # Return success to avoid retries
        return JSONResponse(content={"status": "success"}, status_code=200)


@app.get("/webhook")
async def webhook_verification(request: Request):
    """
    Webhook verification endpoint for WhatsApp Business API
    Required for initial webhook setup
    """
    try:
        # Get query parameters
        params = dict(request.query_params)
        logger.info(f"Webhook verification request: {params}")

        # WhatsApp Business API verification
        hub_mode = params.get("hub.mode")
        hub_challenge = params.get("hub.challenge")
        hub_verify_token = params.get("hub.verify_token")

        verify_token = os.getenv("WEBHOOK_VERIFY_TOKEN", "your_verify_token")

        if hub_mode == "subscribe" and hub_verify_token == verify_token:
            logger.info("✅ Webhook verified successfully")
            return Response(content=hub_challenge, media_type="text/plain")
        else:
            logger.warning("❌ Webhook verification failed")
            raise HTTPException(status_code=403, detail="Verification failed")

    except Exception as e:
        logger.error(f"Error in webhook verification: {str(e)}")
        raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/process-async")
async def process_async(request: Request, db: Session = Depends(get_db)):
    """
    ASYNC processing endpoint - called by QStash
    Can take 5-60 seconds, NO timeout!

    This endpoint is called by QStash after /webhook queues the message
    """
    agent_service = None
    phone_number = None

    try:
        logger.info("🔄 /process-async called by QStash")

        # Get data from QStash
        data = await request.json()

        phone_number = data.get("phone")
        user_message = data.get("message")
        message_sid = data.get("message_sid")
        user_name = data.get("user_name")

        logger.info(f"📱 Processing message from {phone_number}")
        logger.info(f"💬 Message: {user_message[:100]}...")

        # Initialize services
        agent_service = AgentService(db)
        whatsapp_service = WhatsAppService()

        logger.info(f"🤖 Calling AI agent...")

        # Process with AI (can take 5-30 seconds)
        response_text = await agent_service.process_message(
            phone_number=phone_number,
            user_message=user_message,
            message_sid=message_sid,
            user_name=user_name,
        )

        logger.info(f"✅ AI response generated: {response_text[:100]}...")
        logger.info(f"📤 Sending to WhatsApp via AiSensy...")

        # Send response via AiSensy WhatsApp API
        success = whatsapp_service.send_message_using_Twilio(phone_number, response_text)

        if success:
            logger.info(f"✅ Message sent successfully to {phone_number}")
        else:
            logger.error(f"❌ Failed to send message to {phone_number}")

        return {"status": "success", "phone": phone_number, "sent": success}

    except Exception as e:
        logger.error(f"❌ Error in async processing: {str(e)}", exc_info=True)

        # CRITICAL: Rollback database on ANY error to prevent PendingRollbackError
        try:
            db.rollback()
            logger.info("Database session rolled back successfully")
        except Exception as rollback_error:
            logger.error(f"Error during rollback: {rollback_error}")

        # Try to send error message to user
        try:
            if phone_number:
                whatsapp_service = WhatsAppService()
                error_msg = "I apologize, I'm having trouble processing your request. Please try again in a moment."
                whatsapp_service.send_message_using_Twilio(phone_number, error_msg)
        except Exception as msg_error:
            logger.error(f"Failed to send error message to user: {msg_error}")

        # Return error to QStash (will retry if configured)
        return JSONResponse(
            status_code=500, content={"status": "error", "message": str(e)}
        )

    finally:
        # Always cleanup agent service resources
        if agent_service:
            try:
                await agent_service.close()
            except Exception as close_error:
                logger.error(f"Error closing agent service: {close_error}")


@app.post("/send-message")
async def send_message(
    to_number: str = Form(...), message: str = Form(...), db: Session = Depends(get_db)
):
    """
    Manually send a WhatsApp message via AiSensy
    Useful for testing or admin notifications
    """
    try:
        whatsapp_service = WhatsAppService()
        success = whatsapp_service.send_message_using_Twilio(to_number, message)

        if success:
            return {"status": "success", "message": "Message sent successfully"}
        else:
            return {"status": "error", "message": "Failed to send message"}

    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/test-send")
async def test_send_message(phone: str, message: str):
    """
    Test endpoint to send a message directly (no form data)
    """
    try:
        whatsapp_service = WhatsAppService()
        success = whatsapp_service.send_message_using_Twilio(phone, message)
        return {"success": success, "phone": phone}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/config-status")
async def config_status():
    """Check configuration status"""
    return {
        "aisensy_project_id": os.getenv("AISENSY_PROJECT_ID", "not_set"),
        "aisensy_configured": bool(
            os.getenv("AISENSY_PROJECT_ID") and os.getenv("AISENSY_PROJECT_API_PWD")
        ),
        "whatsapp_business_api_configured": bool(
            os.getenv("WHATSAPP_PHONE_NUMBER_ID") and os.getenv("WHATSAPP_ACCESS_TOKEN")
        ),
        "qstash_configured": bool(QSTASH_TOKEN),
        "qstash_url": QSTASH_URL,
        "base_url": BASE_URL,
        "email_configured": bool(os.getenv("OWNER_EMAIL") and os.getenv("SMTP_SERVER")),
        "travel_studio_configured": bool(os.getenv("TRAVEL_STUDIO_BEARER_TOKEN")),
    }


# Travel Studio API Endpoints

@app.get("/travel-studio/bookings")
async def get_travel_studio_bookings(
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get bookings from Travel Studio API"""
    try:
        travel_studio = get_travel_studio_service()
        bookings = travel_studio.get_bookings(status=status, start_date=start_date, end_date=end_date)
        
        if bookings is not None:
            return {"status": "success", "bookings": bookings, "count": len(bookings)}
        else:
            return {"status": "error", "message": "Failed to fetch bookings"}
    except Exception as e:
        logger.error(f"Error fetching bookings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/travel-studio/bookings/{booking_id}")
async def get_travel_studio_booking(booking_id: str):
    """Get a specific booking from Travel Studio API"""
    try:
        travel_studio = get_travel_studio_service()
        booking = travel_studio.get_booking_by_id(booking_id)
        
        if booking:
            return {"status": "success", "booking": booking}
        else:
            raise HTTPException(status_code=404, detail="Booking not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching booking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/travel-studio/bookings")
async def create_travel_studio_booking(request: Request):
    """Create a new booking in Travel Studio API"""
    try:
        data = await request.json()
        travel_studio = get_travel_studio_service()
        
        booking = travel_studio.create_booking(**data)
        
        if booking:
            return {"status": "success", "booking": booking}
        else:
            return {"status": "error", "message": "Failed to create booking"}
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/travel-studio/rooms/available")
async def get_available_rooms(
    check_in_date: str,
    check_out_date: str,
    room_type: Optional[str] = None
):
    """Get available rooms from Travel Studio API"""
    try:
        travel_studio = get_travel_studio_service()
        rooms = travel_studio.get_available_rooms(
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            room_type=room_type
        )
        
        if rooms is not None:
            return {"status": "success", "rooms": rooms, "count": len(rooms)}
        else:
            return {"status": "error", "message": "Failed to fetch available rooms"}
    except Exception as e:
        logger.error(f"Error fetching available rooms: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/travel-studio/rooms/types")
async def get_room_types():
    """Get room types from Travel Studio API"""
    try:
        travel_studio = get_travel_studio_service()
        room_types = travel_studio.get_room_types()
        
        if room_types is not None:
            return {"status": "success", "room_types": room_types}
        else:
            return {"status": "error", "message": "Failed to fetch room types"}
    except Exception as e:
        logger.error(f"Error fetching room types: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/travel-studio/profile")
async def get_hotel_profile():
    """Get hotel profile from Travel Studio API"""
    try:
        travel_studio = get_travel_studio_service()
        profile = travel_studio.get_hotel_profile()
        
        if profile:
            return {"status": "success", "profile": profile}
        else:
            return {"status": "error", "message": "Failed to fetch hotel profile"}
    except Exception as e:
        logger.error(f"Error fetching hotel profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn

    # Verify required environment variables
    required_vars = ["AISENSY_PROJECT_ID", "AISENSY_PROJECT_API_PWD"]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
        logger.info("Required variables:")
        logger.info("  - AISENSY_PROJECT_ID")
        logger.info("  - AISENSY_PROJECT_API_PWD")
        logger.info("Optional variables:")
        logger.info("  - WHATSAPP_PHONE_NUMBER_ID (for typing indicator)")
        logger.info("  - WHATSAPP_ACCESS_TOKEN (for typing indicator)")
        logger.info("  - QSTASH_TOKEN (for async processing)")
        logger.info("  - BASE_URL (your deployment URL)")
        exit(1)

    logger.info("Starting WhatsApp Agent Server with AiSensy...")
    logger.info(f"AiSensy Project ID: {os.getenv('AISENSY_PROJECT_ID')}")
    logger.info(f"QStash configured: {bool(QSTASH_TOKEN)}")

    uvicorn.run(app, host="0.0.0.0", port=8000)
