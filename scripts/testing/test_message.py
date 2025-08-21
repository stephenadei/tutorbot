#!/usr/bin/env python3
"""
Test sending a message to the bot
"""

import requests
import json
import os
import hmac
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
CW_URL = os.getenv("CW_URL", "https://crm.stephenadei.nl")
CW_ACC_ID = os.getenv("CW_ACC_ID", "1")
CW_HMAC_SECRET = os.getenv("CW_HMAC_SECRET")
WEBHOOK_URL = "https://bot.stephensprivelessen.nl/cw"

def create_webhook_signature(payload, secret):
    """Create HMAC signature for webhook"""
    return hmac.new(
        secret.encode('utf-8'),
        json.dumps(payload, separators=(',', ':')).encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def test_message():
    """Test sending a message to the bot"""
    print(f"🧪 Testing bot with a message...")
    
    # Create a realistic webhook event
    webhook_event = {
        "event": "message_created",
        "message": {
            "id": 999,
            "conversation_id": 2,
            "content": "Hallo, ik wil bijles",
            "message_type": 0,
            "content_type": "text",
            "created_at": "2025-08-19T12:00:00Z",
            "updated_at": "2025-08-19T12:00:00Z"
        },
        "conversation": {
            "id": 2,
            "contact_id": 2,
            "inbox_id": 1,
            "status": "open",
            "created_at": "2025-08-19T12:00:00Z",
            "updated_at": "2025-08-19T12:00:00Z"
        },
        "contact": {
            "id": 2,
            "name": "Test User",
            "email": "test@example.com",
            "phone_number": "+31612345678",
            "created_at": "2025-08-19T12:00:00Z",
            "updated_at": "2025-08-19T12:00:00Z"
        },
        "account": {
            "id": 1,
            "name": "Stephen's Privelessen"
        }
    }
    
    # Create signature
    signature = create_webhook_signature(webhook_event, CW_HMAC_SECRET)
    
    headers = {
        'Content-Type': 'application/json',
        'X-Chatwoot-Signature': signature
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=webhook_event,
            headers=headers
        )
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            print(f"✅ Message sent successfully!")
            return True
        else:
            print(f"❌ Message failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_message()

