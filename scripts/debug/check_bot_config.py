#!/usr/bin/env python3
"""
Check Chatwoot Bot configuration (not webhooks)
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
CW_TOKEN = os.getenv("CW_TOKEN")
WEBHOOK_URL = "https://bot.stephensprivelessen.nl/cw"

def check_bot_configuration():
    """Check current bot configuration"""
    print(f"🤖 Checking Chatwoot Bot configuration...")
    
    headers = {
        'Content-Type': 'application/json',
        'api_access_token': CW_TOKEN
    }
    
    try:
        response = requests.get(
            f"{CW_URL}/api/v1/accounts/{CW_ACC_ID}/bots",
            headers=headers
        )
        
        if response.status_code == 200:
            bots = response.json()
            print(f"✅ Found {len(bots)} bots")
            
            for bot in bots:
                print(f"   - ID: {bot.get('id')}")
                print(f"     Name: {bot.get('name')}")
                print(f"     Type: {bot.get('bot_type')}")
                print(f"     URL: {bot.get('webhook_url')}")
                print(f"     Status: {bot.get('status')}")
                
                # Check if our bot is configured
                if bot.get('webhook_url') == WEBHOOK_URL:
                    print(f"     ✅ Our TutorBot is configured!")
                    return bot
                else:
                    print(f"     ❌ Different URL configured")
                print()
            
            return None
        else:
            print(f"❌ Failed to get bots: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def create_bot():
    """Create bot if it doesn't exist"""
    print(f"🔗 Creating TutorBot...")
    
    headers = {
        'Content-Type': 'application/json',
        'api_access_token': CW_TOKEN
    }
    
    bot_data = {
        "name": "TutorBot",
        "bot_type": "webhook",
        "webhook_url": WEBHOOK_URL,
        "hmac_secret": "e6cffc2ec52cedc73e616746e629d346ca55daee82d0c87286eca62aa8d71393"
    }
    
    try:
        response = requests.post(
            f"{CW_URL}/api/v1/accounts/{CW_ACC_ID}/bots",
            headers=headers,
            json=bot_data
        )
        
        if response.status_code == 200:
            bot = response.json()
            print(f"✅ TutorBot created successfully!")
            print(f"   ID: {bot.get('id')}")
            print(f"   Name: {bot.get('name')}")
            print(f"   URL: {bot.get('webhook_url')}")
            return bot
        else:
            print(f"❌ Failed to create bot: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_webhooks_to_remove():
    """Check for webhooks that should be removed"""
    print(f"🔍 Checking for webhooks to remove...")
    
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
            conflicting_webhooks = []
            
            for webhook in webhooks:
                if webhook.get('url') == WEBHOOK_URL:
                    conflicting_webhooks.append(webhook)
                    print(f"⚠️ Found conflicting webhook:")
                    print(f"   ID: {webhook.get('id')}")
                    print(f"   URL: {webhook.get('url')}")
                    print(f"   Status: {webhook.get('status')}")
            
            if conflicting_webhooks:
                print(f"\n❌ Remove these webhooks to prevent duplicate messages!")
                return conflicting_webhooks
            else:
                print(f"✅ No conflicting webhooks found")
                return []
        else:
            print(f"❌ Failed to get webhooks: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_bot_endpoint():
    """Test bot endpoint with proper signature"""
    print(f"🧪 Testing bot endpoint...")
    
    # Simple test to see if endpoint responds
    try:
        response = requests.get(WEBHOOK_URL, timeout=5)
        print(f"📡 GET Response: {response.status_code}")
        
        # Test POST with minimal data
        test_data = {"test": "bot"}
        response = requests.post(WEBHOOK_URL, json=test_data, timeout=5)
        print(f"📡 POST Response: {response.status_code}")
        
        if response.status_code in [401, 405, 400]:
            print(f"✅ Bot endpoint is responding (expected error for invalid request)")
            return True
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return False

if __name__ == "__main__":
    print("🤖 TutorBot Configuration Checker")
    print("=" * 40)
    
    # Check bot configuration
    bot = check_bot_configuration()
    print()
    
    # Check for conflicting webhooks
    conflicting_webhooks = check_webhooks_to_remove()
    print()
    
    # Test bot endpoint
    test_bot_endpoint()
    print()
    
    # Create bot if needed
    if not bot:
        print("⚠️ TutorBot not found, creating one...")
        create_bot()
    else:
        print("✅ TutorBot is already configured!")
    
    print(f"\n💡 Next steps:")
    print(f"1. Remove any conflicting webhooks from Chatwoot admin panel")
    print(f"2. Send a message to your WhatsApp number to test the bot")
    print(f"3. Monitor logs: docker logs tutorbot_tutorbot_1 -f")
    print(f"4. Check Chatwoot admin panel for bot configuration")

