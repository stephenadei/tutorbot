#!/usr/bin/env python3
"""
Debug webhook configuration and test with real Chatwoot data
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

def test_real_chatwoot_webhook():
    """Test with real Chatwoot webhook data structure"""
    print(f"🧪 Testing with real Chatwoot webhook data...")
    
    # Real Chatwoot webhook event structure
    webhook_event = {
        "event": "message_created",
        "message": {
            "id": 123,
            "conversation_id": 456,
            "content": "Hallo, ik wil bijles",
            "message_type": 0,
            "content_type": "text",
            "created_at": "2025-08-19T12:00:00Z",
            "updated_at": "2025-08-19T12:00:00Z"
        },
        "conversation": {
            "id": 456,
            "contact_id": 789,
            "inbox_id": 1,
            "status": "open",
            "created_at": "2025-08-19T12:00:00Z",
            "updated_at": "2025-08-19T12:00:00Z"
        },
        "contact": {
            "id": 789,
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
            print(f"✅ Webhook with real data successful!")
            return True
        else:
            print(f"❌ Webhook failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_conversation_created_webhook():
    """Test conversation_created event"""
    print(f"💬 Testing conversation_created event...")
    
    webhook_event = {
        "event": "conversation_created",
        "conversation": {
            "id": 456,
            "contact_id": 789,
            "inbox_id": 1,
            "status": "open",
            "created_at": "2025-08-19T12:00:00Z",
            "updated_at": "2025-08-19T12:00:00Z"
        },
        "contact": {
            "id": 789,
            "name": "Test User",
            "email": "test@example.com",
            "phone_number": "+31612345678"
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
            print(f"✅ Conversation created webhook successful!")
            return True
        else:
            print(f"❌ Conversation created webhook failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_chatwoot_connection():
    """Check if we can connect to Chatwoot"""
    print(f"🔗 Checking Chatwoot connection...")
    
    headers = {
        'Content-Type': 'application/json',
        'api_access_token': CW_TOKEN
    }
    
    try:
        response = requests.get(
            f"{CW_URL}/api/v1/accounts/{CW_ACC_ID}",
            headers=headers
        )
        
        if response.status_code == 200:
            account = response.json()
            print(f"✅ Connected to Chatwoot!")
            print(f"   Account: {account.get('name')}")
            print(f"   ID: {account.get('id')}")
            return True
        else:
            print(f"❌ Failed to connect: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_inboxes():
    """Check available inboxes"""
    print(f"📥 Checking inboxes...")
    
    headers = {
        'Content-Type': 'application/json',
        'api_access_token': CW_TOKEN
    }
    
    try:
        response = requests.get(
            f"{CW_URL}/api/v1/accounts/{CW_ACC_ID}/inboxes",
            headers=headers
        )
        
        if response.status_code == 200:
            inboxes = response.json()
            print(f"✅ Found {len(inboxes)} inboxes")
            
            for inbox in inboxes:
                print(f"   - ID: {inbox.get('id')}")
                print(f"     Name: {inbox.get('name')}")
                print(f"     Type: {inbox.get('channel_type')}")
                print(f"     Status: {inbox.get('status')}")
                print()
            
            return inboxes
        else:
            print(f"❌ Failed to get inboxes: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_webhook_config():
    """Check webhook configuration via API"""
    print(f"🔧 Checking webhook configuration...")
    
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
                print()
            
            return webhooks
        else:
            print(f"❌ Failed to get webhooks: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("🔍 TutorBot Webhook Debug Tool")
    print("=" * 40)
    
    # Check Chatwoot connection
    if check_chatwoot_connection():
        print()
        
        # Check inboxes
        check_inboxes()
        print()
        
        # Check webhook configuration
        webhooks = check_webhook_config()
        print()
        
        # Test webhooks with real data
        test_conversation_created_webhook()
        print()
        
        test_real_chatwoot_webhook()
        print()
    
    print(f"\n💡 Troubleshooting steps:")
    print(f"1. Check if webhook is configured in Chatwoot admin panel")
    print(f"2. Verify HMAC secret matches: {CW_HMAC_SECRET}")
    print(f"3. Check if WhatsApp integration is active in Chatwoot")
    print(f"4. Send a test message and check logs: docker logs tutorbot_tutorbot_1 -f")
    print(f"5. Verify webhook URL is accessible: {WEBHOOK_URL}")

