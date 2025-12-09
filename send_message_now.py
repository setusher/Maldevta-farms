#!/usr/bin/env python3
"""
Send WhatsApp message from Maldevta Farms Bot to your number
Uses WhatsApp Cloud API (Meta/Facebook)
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
AGENT_NUMBER = "+17744451439"  # Your WhatsApp Business number
YOUR_NUMBER = "919334391959"   # Your personal number (no + needed)

# Get credentials from .env
phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
api_version = os.getenv('WHATSAPP_API_VERSION', 'v24.0')

# WhatsApp Cloud API endpoint
url = f'https://graph.facebook.com/{api_version}/{phone_number_id}/messages'

# Headers
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Message data
data = {
    'messaging_product': 'whatsapp',
    'to': YOUR_NUMBER,
    'type': 'text',
    'text': {
        'body': '''🏨 *Maldevta Farms WhatsApp Bot*

Hello! I'm your AI-powered booking assistant.

✅ Bot is now active and ready!

I can help you with:
• Check room availability
• Make reservations
• View your bookings
• Get hotel information

Try asking me: "Check availability for December 15 to 17"'''
    }
}

print("="*60)
print("  SENDING WHATSAPP MESSAGE")
print("="*60)
print(f"From: {AGENT_NUMBER} (Maldevta Farms Bot)")
print(f"To: +91{YOUR_NUMBER}")
print(f"Using: WhatsApp Cloud API")
print("\nSending message...")

try:
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS! Message sent!")
        print(f"Message ID: {result.get('messages', [{}])[0].get('id', 'N/A')}")
        print(f"\nCheck your WhatsApp at +91{YOUR_NUMBER}")
        print("You should receive the message within seconds!")
    else:
        print(f"\n❌ FAILED: HTTP {response.status_code}")
        print(f"Error: {response.text}")
        
        if response.status_code == 400:
            print("\n💡 Possible issues:")
            print("1. Your number might not be registered with WhatsApp Business")
            print("2. You may need to send a message to the bot first")
            print("3. The access token might be expired")
        elif response.status_code == 403:
            print("\n💡 Access denied - check your WhatsApp Business API permissions")
            
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Check your .env file has WHATSAPP_ACCESS_TOKEN")
    print("2. Verify WHATSAPP_PHONE_NUMBER_ID is correct")
    print("3. Make sure your WhatsApp Business account is active")

print("="*60)
