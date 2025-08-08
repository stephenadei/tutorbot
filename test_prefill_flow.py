#!/usr/bin/env python3
"""
Test script to send a message with intake information
"""

import requests
import json
import os

# Load environment variables
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value

# Configuration
CW_URL = os.getenv("CW_URL", "https://crm.stephenadei.nl")
ACC_ID = os.getenv("CW_ACC_ID", "1")
ADMIN_TOKEN = os.getenv("CW_ADMIN_TOKEN")

def send_test_message():
    """Send a test message with intake information"""
    
    # Test message with intake information
    test_message = """Maria
HAVO
Wiskunde
Wiskunde A
Anders
Spinoza Lyceum
5,2
verbeteren van vaardigheden voor toekomstige toetsen
woensdagmiddag
Science Park
Roberta Sandrelli
gemiddeld"""
    
    # Create a new conversation and send message
    conversation_data = {
        "inbox_id": 1,
        "contact_id": 2,  # Use existing contact
        "message": {
            "content": test_message,
            "message_type": "incoming"
        }
    }
    
    url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/conversations"
    headers = {
        "api_access_token": ADMIN_TOKEN,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=conversation_data)
        if response.status_code == 200:
            print("✅ Test message sent successfully!")
            print(f"📝 Message: {test_message[:100]}...")
            print("🔍 Check the bot logs to see the prefill flow")
        else:
            print(f"❌ Failed to send message: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error sending message: {e}")

if __name__ == "__main__":
    print("🧪 Testing Prefill Flow")
    print("=" * 50)
    send_test_message()
