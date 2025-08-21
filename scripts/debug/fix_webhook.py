#!/usr/bin/env python3
"""
Fix webhook configuration and test with proper signature
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
CW_TOKEN = os.getenv("CW_TOKEN")
CW_HMAC_SECRET = os.getenv("CW_HMAC_SECRET")
WEBHOOK_URL = "https://bot.stephensprivelessen.nl/cw"

def create_webhook_signature(payload, secret):
    """Create HMAC signature for webhook"""
    return hmac.new(
        secret.encode('utf-8'),
        json.dumps(payload, separators=(',', ':')).encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def test_webhook_with_signature():
    """Test webhook with proper signature"""
    print(f"🔐 Testing webhook with proper signature...")
    
    # Create a realistic webhook event
    webhook_event = {
        "event": "conversation_created",
        "conversation": {
            "id": 123,
            "contact_id": 456,
            "inbox_id": 1,
            "status": "open",
            "created_at": "2025-08-19T12:00:00Z",
            "updated_at": "2025-08-19T12:00:00Z"
        },
        "contact": {
            "id": 456,
            "name": "Test User",
            "email": "test@example.com",
            "phone_number": "+31612345678"
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
            print(f"✅ Webhook with signature successful!")
            return True
        else:
            print(f"❌ Webhook failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_webhook_configuration():
    """Check current webhook configuration"""
    print(f"⚙️ Checking webhook configuration...")
    
    headers = {
        'Content-Type': 'application/json',
        'api_access_token': CW_TOKEN
    }
    
    try:
        response = requests.get(
            f"{CW_URL}/api/v1/accounts/{CW_ACC_ID}/webhooks",
            headers=headers
        )
        
        if response.status_code == 200:
            webhooks = response.json()
            print(f"✅ Found {len(webhooks)} webhooks")
            
            for webhook in webhooks:
                print(f"   - ID: {webhook.get('id')}")
                print(f"     URL: {webhook.get('url')}")
                print(f"     Status: {webhook.get('status')}")
                print(f"     Events: {webhook.get('subscriptions', [])}")
                
                # Check if our webhook URL is configured
                if webhook.get('url') == WEBHOOK_URL:
                    print(f"     ✅ Our webhook is configured!")
                else:
                    print(f"     ❌ Different URL configured")
                print()
            
            return webhooks
        else:
            print(f"❌ Failed to get webhooks: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def create_webhook():
    """Create webhook if it doesn't exist"""
    print(f"🔗 Creating webhook...")
    
    headers = {
        'Content-Type': 'application/json',
        'api_access_token': CW_TOKEN
    }
    
    webhook_data = {
        "url": WEBHOOK_URL,
        "subscriptions": [
            "conversation_created",
            "message_created",
            "conversation_status_changed"
        ]
    }
    
    try:
        response = requests.post(
            f"{CW_URL}/api/v1/accounts/{CW_ACC_ID}/webhooks",
            headers=headers,
            json=webhook_data
        )
        
        if response.status_code == 200:
            webhook = response.json()
            print(f"✅ Webhook created successfully!")
            print(f"   ID: {webhook.get('id')}")
            print(f"   URL: {webhook.get('url')}")
            return webhook
        else:
            print(f"❌ Failed to create webhook: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_bot_status():
    """Check if bot is running and healthy"""
    print(f"🤖 Checking bot status...")
    
    try:
        response = requests.get("https://bot.stephensprivelessen.nl/health", timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Bot is healthy!")
            return True
        else:
            print(f"❌ Bot health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Bot health check error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 TutorBot Webhook Fix Tool")
    print("=" * 40)
    
    # Check bot status
    if check_bot_status():
        print()
        
        # Check webhook configuration
        webhooks = check_webhook_configuration()
        print()
        
        # Create webhook if needed
        if not webhooks:
            print("⚠️ No webhooks found, creating one...")
            create_webhook()
        else:
            # Check if our webhook is configured
            our_webhook = None
            for webhook in webhooks:
                if webhook.get('url') == WEBHOOK_URL:
                    our_webhook = webhook
                    break
            
            if not our_webhook:
                print("⚠️ Our webhook not found, creating one...")
                create_webhook()
        
        print()
        
        # Test webhook with signature
        test_webhook_with_signature()
    
    print(f"\n💡 Next steps:")
    print(f"1. Send a message to your WhatsApp number")
    print(f"2. Check the logs: docker logs tutorbot_tutorbot_1 -f")
    print(f"3. Verify webhook is configured in Chatwoot admin panel")

