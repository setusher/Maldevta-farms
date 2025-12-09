#!/usr/bin/env python3
"""
Send WhatsApp message using Twilio
From: +1 (774) 445-1439 (Maldevta Farms Bot)
To: +91 9334391959 (Your number)
"""

from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
AGENT_NUMBER = "+17744451439"  # Your WhatsApp Business number
YOUR_NUMBER = "+919334391959"   # Your personal number

# Get Twilio credentials
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')

print("="*60)
print("  SENDING WHATSAPP MESSAGE VIA TWILIO")
print("="*60)
print(f"From: {AGENT_NUMBER} (Maldevta Farms Bot)")
print(f"To: {YOUR_NUMBER}")
print(f"Using: Twilio WhatsApp API")
print("\nSending message...")

try:
    client = Client(account_sid, auth_token)
    
    message = client.messages.create(
        from_=f'whatsapp:{AGENT_NUMBER}',
        body='''🏨 *Maldevta Farms WhatsApp Bot*

Hello! I'm your AI-powered booking assistant.

✅ Bot is now active and ready!

I can help you with:
• Check room availability  
• Make reservations
• View your bookings
• Get hotel information

Try asking me: "Check availability for December 15 to 17"

Reply to this message to start chatting!''',
        to=f'whatsapp:{YOUR_NUMBER}'
    )
    
    print("\n✅ SUCCESS! Message sent via Twilio!")
    print(f"Message SID: {message.sid}")
    print(f"Status: {message.status}")
    print(f"\nCheck your WhatsApp at {YOUR_NUMBER}")
    print("You should receive the message within seconds!")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("\nPossible issues:")
    print("1. Your Twilio WhatsApp Sender needs to be activated")
    print("2. You may need to join the Twilio sandbox first")
    print("3. Check your Twilio account status")
    print("\nTo join Twilio sandbox:")
    print(f"Send 'join <your-sandbox-code>' to whatsapp:{AGENT_NUMBER}")

print("="*60)
