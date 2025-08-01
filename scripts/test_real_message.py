#!/usr/bin/env python3
"""
Test Real Message Response
Sends a message to an existing conversation to test bot response.
"""

import os
import requests
import json

# Get environment variables
CW_URL = os.getenv("CW_URL", "https://crm.stephenadei.nl")
ACC = os.getenv("CW_ACC_ID", "1")
ADMIN_TOK = os.getenv("CW_ADMIN_TOKEN", "mCNRQJzK4KbVuinP7NszBTug")
BOT_URL = "http://localhost:8000/cw"

def send_test_message(conversation_id, contact_id, message):
    """Send a test message to trigger bot response"""
    # First, send message via Chatwoot API
    url = f"{CW_URL}/api/v1/accounts/{ACC}/conversations/{conversation_id}/messages"
    headers = {
        "api_access_token": ADMIN_TOK,
        "Content-Type": "application/json"
    }
    data = {
        "content": message,
        "message_type": "incoming"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"📨 Message sent to Chatwoot: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Message sent successfully: '{message}'")
            
            # Now trigger the bot webhook
            webhook_data = {
                "event": "message_created",
                "conversation": {
                    "id": conversation_id
                },
                "sender": {
                    "id": contact_id
                },
                "content": message
            }
            
            webhook_headers = {
                "Content-Type": "application/json"
            }
            
            webhook_response = requests.post(
                BOT_URL, 
                headers=webhook_headers, 
                data=json.dumps(webhook_data)
            )
            
            print(f"🤖 Bot webhook response: {webhook_response.status_code}")
            if webhook_response.status_code == 200:
                print("✅ Bot processed the message")
            else:
                print(f"❌ Bot webhook failed: {webhook_response.text}")
                
        else:
            print(f"❌ Failed to send message: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main test function"""
    print("🧪 Real Message Test")
    print("=" * 50)
    
    # Use existing conversation (Conv:49 Contact:31 from logs)
    conversation_id = 49
    contact_id = 31
    
    print(f"📝 Testing with conversation {conversation_id} and contact {contact_id}")
    
    # Test different messages
    test_messages = [
        "Hello",
        "🇳🇱 Nederlands", 
        "nl",
        "🇬🇧 English",
        "en"
    ]
    
    for message in test_messages:
        print(f"\n🔍 Testing message: '{message}'")
        send_test_message(conversation_id, contact_id, message)
        
        # Wait a moment between messages
        import time
        time.sleep(2)
    
    print(f"\n✅ Test completed! Check the bot logs to see responses.")

if __name__ == "__main__":
    main() 