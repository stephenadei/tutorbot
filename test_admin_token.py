#!/usr/bin/env python3
"""
Test admin token vs bot token with Chatwoot API endpoints
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
CW_ADMIN_TOKEN = os.getenv("CW_ADMIN_TOKEN", "CMv7SMDTMqV4HCHaJoHVoUjb")

def test_token_with_endpoint(endpoint, description, token, token_name):
    """Test token with specific endpoint"""
    print(f"🔍 Testing {token_name}: {description}")
    print(f"   URL: {CW_URL}{endpoint}")
    
    headers = {
        'Content-Type': 'application/json',
        'api_access_token': token
    }
    
    try:
        response = requests.get(f"{CW_URL}{endpoint}", headers=headers)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success!")
            
            if isinstance(data, dict):
                print(f"   Data: {json.dumps(data, indent=2)}")
            elif isinstance(data, list):
                print(f"   Items: {len(data)}")
                if data:
                    print(f"   First item: {json.dumps(data[0], indent=2)}")
            
            return True
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_both_tokens():
    """Test both bot token and admin token"""
    print("🔑 Token Comparison Test")
    print("=" * 50)
    
    endpoints = [
        ("/api/v1/accounts/1", "Account Info"),
        ("/api/v1/accounts/1/inboxes", "Inboxes"),
        ("/api/v1/accounts/1/conversations", "Conversations"),
        ("/api/v1/accounts/1/contacts", "Contacts"),
        ("/api/v1/accounts/1/agents", "Agents"),
        ("/api/v1/accounts/1/webhooks", "Webhooks"),
    ]
    
    print(f"🤖 Bot Token: {CW_TOKEN[:10]}...")
    print(f"👑 Admin Token: {CW_ADMIN_TOKEN[:10]}...")
    print()
    
    for endpoint, description in endpoints:
        print(f"\n{'-' * 30}")
        print(f"📋 Testing: {description}")
        print(f"{'-' * 30}")
        
        # Test bot token
        bot_success = test_token_with_endpoint(endpoint, description, CW_TOKEN, "Bot Token")
        print()
        
        # Test admin token
        admin_success = test_token_with_endpoint(endpoint, description, CW_ADMIN_TOKEN, "Admin Token")
        
        if bot_success and admin_success:
            print("   🟢 Both tokens work!")
        elif admin_success and not bot_success:
            print("   🟡 Only admin token works")
        elif bot_success and not admin_success:
            print("   🟡 Only bot token works")
        else:
            print("   🔴 Neither token works")

def test_webhook_creation():
    """Test if we can create webhooks with admin token"""
    print(f"\n{'=' * 50}")
    print("🔗 Testing Webhook Creation with Admin Token")
    print("=" * 50)
    
    headers = {
        'Content-Type': 'application/json',
        'api_access_token': CW_ADMIN_TOKEN
    }
    
    webhook_data = {
        "url": "https://bot.stephensprivelessen.nl/cw",
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
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            webhook = response.json()
            print(f"✅ Webhook created successfully!")
            print(f"   ID: {webhook.get('id')}")
            print(f"   URL: {webhook.get('url')}")
            print(f"   Status: {webhook.get('status')}")
            return webhook
        else:
            print(f"❌ Failed to create webhook: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def list_existing_webhooks():
    """List existing webhooks with admin token"""
    print(f"\n{'=' * 50}")
    print("📋 Listing Existing Webhooks with Admin Token")
    print("=" * 50)
    
    headers = {
        'Content-Type': 'application/json',
        'api_access_token': CW_ADMIN_TOKEN
    }
    
    try:
        response = requests.get(
            f"{CW_URL}/api/v1/accounts/{CW_ACC_ID}/webhooks",
            headers=headers
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
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
    # Test both tokens
    test_both_tokens()
    
    # List existing webhooks
    existing_webhooks = list_existing_webhooks()
    
    # Try to create webhook if none exist
    if not existing_webhooks:
        print("\n⚠️ No webhooks found, attempting to create one...")
        test_webhook_creation()
    else:
        print("\n✅ Webhooks already exist!")
    
    print(f"\n💡 Next steps:")
    print(f"1. If admin token works, we can configure webhooks via API")
    print(f"2. If not, configure webhook manually in Chatwoot admin panel")
    print(f"3. Test with WhatsApp message after webhook is configured")

