#!/usr/bin/env python3
"""
Test Input Select Functionality
Tests the Chatwoot input_select format to see why it's not working.
"""

import os
import requests
import json

# Get environment variables
CW_URL = os.getenv("CW_URL", "https://crm.stephenadei.nl")
ACC = os.getenv("CW_ACC_ID", "1")
TOK = os.getenv("CW_TOKEN", "R3vx2s67k7hUpXsLWqDrE6nR")
ADMIN_TOK = os.getenv("CW_ADMIN_TOKEN", "mCNRQJzK4KbVuinP7NszBTug")

def test_input_select(conversation_id):
    """Test input_select format"""
    url = f"{CW_URL}/api/v1/accounts/{ACC}/conversations/{conversation_id}/messages"
    headers = {
        "api_access_token": TOK,
        "Content-Type": "application/json"
    }
    
    # Test different formats
    test_cases = [
        {
            "name": "Chatwoot input_select format",
            "data": {
                "content": "🌍 In welke taal wil je communiceren? 🇳🇱 Nederlands · 🇬🇧 English",
                "content_type": "input_select",
                "content_attributes": {
                    "items": [
                        {"title": "🇳🇱 Nederlands", "value": "lang_nl"},
                        {"title": "🇬🇧 English", "value": "lang_en"}
                    ]
                },
                "message_type": "outgoing",
                "private": False
            }
        },
        {
            "name": "Quick replies format",
            "data": {
                "content": "🌍 In welke taal wil je communiceren? 🇳🇱 Nederlands · 🇬🇧 English",
                "message_type": "outgoing",
                "content_attributes": {
                    "quick_replies": [
                        {"title": "🇳🇱 Nederlands", "payload": "lang_nl"},
                        {"title": "🇬🇧 English", "payload": "lang_en"}
                    ]
                }
            }
        },
        {
            "name": "WhatsApp button format",
            "data": {
                "content": "🌍 In welke taal wil je communiceren? 🇳🇱 Nederlands · 🇬🇧 English",
                "message_type": "outgoing",
                "content_attributes": {
                    "content_type": "button",
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "lang_nl",
                                "title": "🇳🇱 Nederlands"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "lang_en",
                                "title": "🇬🇧 English"
                            }
                        }
                    ]
                }
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['name']}")
        print(f"📨 URL: {url}")
        print(f"📋 Data: {json.dumps(test_case['data'], indent=2)}")
        
        try:
            response = requests.post(url, headers=headers, json=test_case['data'])
            print(f"📊 Status: {response.status_code}")
            print(f"📄 Response: {response.text[:200]}")
            
            if response.status_code == 200:
                print(f"✅ SUCCESS: {test_case['name']}")
            else:
                print(f"❌ FAILED: {test_case['name']}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print("-" * 50)

def create_test_conversation():
    """Create a test conversation"""
    # First create a contact
    contact_url = f"{CW_URL}/api/v1/accounts/{ACC}/contacts"
    contact_headers = {
        "api_access_token": ADMIN_TOK,
        "Content-Type": "application/json"
    }
    import time
    timestamp = int(time.time())
    phone_number = f"+316{timestamp % 100000000:08d}"
    
    contact_data = {
        "name": "Test Input Select",
        "phone_number": phone_number
    }
    
    try:
        response = requests.post(contact_url, headers=contact_headers, json=contact_data)
        if response.status_code == 200:
            contact = response.json()
            contact_id = contact.get('payload', {}).get('contact', {}).get('id')
            print(f"✅ Created test contact: {contact_id}")
            
            # Create conversation
            conv_url = f"{CW_URL}/api/v1/accounts/{ACC}/conversations"
            conv_data = {
                "contact_id": contact_id,
                "inbox_id": 2  # WhatsApp inbox
            }
            
            response = requests.post(conv_url, headers=contact_headers, json=conv_data)
            print(f"📨 Conversation creation response: {response.status_code} - {response.text[:200]}")
            if response.status_code == 200:
                conversation = response.json()
                conv_id = conversation.get('payload', {}).get('conversation', {}).get('id')
                print(f"✅ Created test conversation: {conv_id}")
                return conv_id, contact_id
            else:
                print(f"❌ Failed to create conversation: {response.status_code}")
                return None, contact_id
        else:
            print(f"❌ Failed to create contact: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        return None, None

def main():
    """Main test function"""
    print("🧪 Input Select Test")
    print("=" * 50)
    
    # Create test conversation
    conv_id, contact_id = create_test_conversation()
    
    if conv_id:
        print(f"\n📝 Testing with conversation {conv_id}")
        test_input_select(conv_id)
        
        # Cleanup
        print(f"\n🧹 Cleaning up test data...")
        if conv_id:
            requests.delete(f"{CW_URL}/api/v1/accounts/{ACC}/conversations/{conv_id}", 
                          headers={"api_access_token": ADMIN_TOK})
        if contact_id:
            requests.delete(f"{CW_URL}/api/v1/accounts/{ACC}/contacts/{contact_id}", 
                          headers={"api_access_token": ADMIN_TOK})
        print("✅ Cleanup completed")
    else:
        print("❌ Cannot test without conversation")

if __name__ == "__main__":
    main() 