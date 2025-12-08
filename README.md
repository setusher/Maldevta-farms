# WhatsApp Reservation Agent - Maldevta Farms

AI-powered WhatsApp chatbot for hotel reservations using Google Gemini AI and Twilio.

## Features

- 🤖 Natural language processing with Google Gemini 2.5 Flash
- 📱 WhatsApp integration via Twilio
- 🏨 Complete hotel reservation system for Maldevta Farms, Dehradun
- 💾 Conversation memory and logging
- 🔧 Integrated tools for bookings, events, and more
- 📊 Analytics and conversation tracking
- 🌿 Nature resort with pinewood cottages and outdoor experiences

## Hotel Information

- **Name:** Maldevta Farms
- **Location:** Maldevta, Dehradun, Uttarakhand
- **Description:** A peaceful riverside nature resort with pinewood cottages, hill views, open lawns, and outdoor learning experiences
- **Distance:** ~17 km from Dehradun city center, <20 km from airport
- **Contact:** +1 (774) 445-1439

## Prerequisites

- Python 3.9+
- PostgreSQL database
- Twilio account with WhatsApp enabled
- Google API key (Gemini)
- Your tools API deployed at https://maldevtafarmsagent.vercel.app

## Installation

1. **Clone the repository:**
```bash
cd whatsapp-agent
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up PostgreSQL database:**
```bash
# Create database
createdb whatsapp_agent

# Or using psql
psql -U postgres
CREATE DATABASE whatsapp_agent;
```

5. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your credentials
```

Required environment variables:
```
DATABASE_URL=postgresql://user:password@localhost:5432/whatsapp_agent
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+17744451439
GOOGLE_API_KEY=your_google_api_key
TOOLS_API_BASE_URL=https://maldevtafarmsagent.vercel.app
```

## Running the Server

**Development mode:**
```bash
python server.py
```

**Production mode:**
```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

The server will start on `http://0.0.0.0:8000`

## Twilio Webhook Setup

1. Go to Twilio Console > Messaging > Settings > WhatsApp Sandbox
2. Set webhook URL: `https://your-domain.com/webhook`
3. Method: POST
4. Save configuration

For local testing with ngrok:
```bash
ngrok http 8000
# Use the ngrok URL: https://xxxxx.ngrok.io/webhook
```

## API Endpoints

### Core Endpoints

- `POST /webhook` - WhatsApp webhook (receives messages)
- `GET /` - Health check
- `GET /health` - Health status

### Management Endpoints

- `POST /send-message` - Send manual WhatsApp message
- `GET /conversations/{phone_number}` - Get conversation history
- `GET /tool-calls/{phone_number}` - Get tool call logs
- `GET /stats` - System statistics
- `DELETE /conversations/{phone_number}` - Delete conversation data

**Available Rooms:**
- **Deluxe Room:** ₹4,725/night (incl. breakfast for 2 adults + GST)
- **Luxury Pinewood Cottage:** ₹7,350/night (incl. breakfast for 2 adults + GST)
- **Luxury Pinewood Cottage with Bathtub:** ₹7,875/night (incl. breakfast for 2 adults + GST)

**Total Inventory:** 10 rooms (2 Deluxe, 4 Cottages, 4 Bathtub Cottages)

**Important Policies:**
- **All rates include breakfast for 2 adults** (always mention this)
- Extra bed: ₹1,500 with breakfast / ₹1,000 without breakfast
- 5% GST on all plans
- **Full payment required upfront** (no token/no hold)
- Payment via Razorpay link only

**Cancellation Policy:**
- 72+ hours before check-in: 100% refund
- 48 hours before check-in: 50% refund
- 24 hours before check-in: 25% refund
- Less than 24 hours: No refund

**Special Notes:**
- Swimming pool currently closed for renovation
- Events and group bookings handled by reservations team (escalate)

## Available Tools

The agent can use these tools:

**Room Booking:**
- `check_availability` - Check room availability
- `create_booking_reservation` - Create room booking
- `get_all_room_reservations` - List all bookings

**Events:**
- `create_event_inquiry` - Create event inquiry
- `get_all_event_inquiries` - List event inquiries

**General:**
- `lead_gen` - Generate lead
- `human_followup` - Schedule human callback
- `confirm_payment_details` - Check payment status
- `request_update_or_cancel` - Send cancellation/update request to hotel team

**Note:** No hourly bookings or day outing packages available - only overnight stays

## Example Conversations

**Room Booking:**
```
User: Hi, I need a room for 2 people from 20th to 22nd December
Agent: Yes sir/ma'am! How many rooms do you need for 2 guests?
User: One room should be fine
Agent: Great! I'd recommend our Deluxe Room at ₹4,725 per night (breakfast included for 2 adults). For 2 nights that's ₹9,450 total. May I have your name?
User: Rajesh Kumar
Agent: Thank you, Mr. Rajesh! To confirm your booking, full advance payment is required through our Razorpay link. Creating your booking now.
[Books reservation]
Agent: Done! Payment link sent to your WhatsApp. Once payment is complete, your reservation is confirmed!
```

**Event Inquiry:**
```
User: Can you host a wedding for 150 people?
Agent: For any event or group booking, our reservations team handles customized plans. I'll connect you to them for accurate details. May I have your name and when you're planning this?
User: My name is Priya, planning for March 2025
Agent: Thank you, Ms. Priya! I've noted your wedding inquiry for 150 guests in March 2025. Our team will reach out with a customized quote.
```

## Database Schema

**Tables:**
- `conversations` - Conversation tracking
- `messages` - All messages (inbound/outbound)
- `tool_calls` - Tool execution logs
- `agent_memory` - User preferences and context

## Monitoring & Logs

View logs:
```bash
tail -f server.log
```

Check statistics:
```bash
curl http://localhost:8000/stats
```

## Troubleshooting

**Database connection issues:**
- Verify PostgreSQL is running: `pg_isready`
- Check DATABASE_URL in .env
- Ensure database exists: `psql -l`

**Twilio webhook not receiving:**
- Check webhook URL is publicly accessible
- Verify Twilio webhook configuration
- Check server logs for errors

**Tool calls failing:**
- Verify TOOLS_API_BASE_URL is correct
- Check API is accessible: `curl https://maldevtafarmsagent.vercel.app/health`
- Review tool_calls table for error messages

## Production Deployment

**Using Docker:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Using systemd:**
```ini
[Unit]
Description=WhatsApp Agent
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/whatsapp-agent
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

**Using Heroku:**
```bash
# Create Procfile
echo "web: uvicorn server:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

## Security Best Practices

1. **Never commit .env file** - Keep credentials secret
2. **Use environment variables** - For all sensitive data
3. **Enable HTTPS** - In production
4. **Validate inputs** - Sanitize user data
5. **Rate limiting** - Prevent abuse
6. **Monitor logs** - Track suspicious activity

## Support

For issues or questions:
- Check logs: `tail -f server.log`
- Review conversation history: `GET /conversations/{phone_number}`
- Check tool calls: `GET /tool-calls/{phone_number}`

## License

MIT License - Feel free to modify and use for your projects.