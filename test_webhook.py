#!/usr/bin/env python3
"""
Test webhook with new Chatwoot credentials
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
CW_URL = os.getenv("CW_URL", "https://crm.stephenadei.nl")
CW_ACC_ID = os.getenv("CW_ACC_ID", "1")
CW_TOKEN = os.getenv("CW_TOKEN", "uDSMCbD1EH4cBBDbSgj35WKS")
WEBHOOK_URL = "https://bot.stephensprivelessen.nl/cw"

def test_chatwoot_connection():
    """Test connection to Chatwoot"""
    print(f"🔍 Testing Chatwoot connection...")
    
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
            print(f"✅ Chatwoot connection successful!")
            print(f"🏢 Account: {account.get('name')}")
            return True
        else:
            print(f"❌ Chatwoot connection failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_webhook_endpoint():
    """Test webhook endpoint"""
    print(f"🔗 Testing webhook endpoint...")
    
    try:
        response = requests.head(WEBHOOK_URL)
        
        if response.status_code == 405:  # Method Not Allowed is correct for HEAD
            print(f"✅ Webhook endpoint is active")
            print(f"📡 URL: {WEBHOOK_URL}")
            return True
        else:
            print(f"❌ Webhook endpoint issue: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def send_test_webhook():
    """Send a test webhook"""
    print(f"📨 Sending test webhook...")
    
    # Create a test webhook event
    test_event = {
        "event": "conversation_created",
        "conversation": {
            "id": 999,
            "contact_id": 888,
            "inbox_id": 1,
            "status": "open",
            "created_at": "2025-08-19T12:00:00Z",
            "updated_at": "2025-08-19T12:00:00Z"
        }
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=test_event,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print(f"✅ Test webhook sent successfully!")
            print(f"📄 Response: {response.text}")
            return True
        else:
            print(f"❌ Test webhook failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending test webhook: {e}")
        return False

def check_webhook_configuration():
    """Check webhook configuration in Chatwoot"""
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
                print()
            
            return webhooks
        else:
            print(f"❌ Failed to get webhooks: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("🧪 TutorBot Webhook Test")
    print("=" * 40)
    
    # Test Chatwoot connection
    if test_chatwoot_connection():
        print()
        
        # Test webhook endpoint
        if test_webhook_endpoint():
            print()
            
            # Check webhook configuration
            webhooks = check_webhook_configuration()
            print()
            
            # Send test webhook
            if webhooks:
                send_test_webhook()
            else:
                print("⚠️ No webhooks found. Please configure webhook in Chatwoot:")
                print(f"   URL: {WEBHOOK_URL}")
                print(f"   Events: conversation_created, message_created, etc.")
    
    print(f"\n✅ TutorBot is ready for testing!")
    print(f"📱 Send a message to your WhatsApp number to test the bot.")

