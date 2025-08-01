#!/usr/bin/env python3
"""
Test Bot with Real Conversation
Creates a real conversation in Chatwoot and tests message sending.
"""

import os
import requests
import json
import time
from datetime import datetime

# Get environment variables
CW_URL = os.getenv("CW_URL", "https://crm.stephenadei.nl")
ACC = os.getenv("CW_ACC_ID", "1")
ADMIN_TOK = os.getenv("CW_ADMIN_TOKEN", "mCNRQJzK4KbVuinP7NszBTug")
BOT_TOK = os.getenv("CW_TOKEN", "R3vx2s67k7hUpXsLWqDrE6nR")

def create_test_contact():
    """Create a test contact"""
    url = f"{CW_URL}/api/v1/accounts/{ACC}/contacts"
    headers = {
        "api_access_token": ADMIN_TOK,
        "Content-Type": "application/json"
    }
    # Use timestamp to make phone number unique
    timestamp = int(datetime.now().timestamp())
    phone_number = f"+316{timestamp % 100000000:08d}"
    
    data = {
        "name": "Test Bot User",
        "phone_number": phone_number,
        "custom_attributes": {
            "language": "nl",
            "segment": "new"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"📨 Contact creation response: {response.status_code} - {response.text[:200]}")
        if response.status_code == 200:
            contact = response.json()
            contact_id = contact.get('id') or contact.get('payload', {}).get('contact', {}).get('id')
            if contact_id:
                print(f"✅ Created test contact: {contact_id}")
                return contact_id
            else:
                print(f"❌ No contact ID in response: {contact}")
                return None
        else:
            print(f"❌ Failed to create contact: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating contact: {e}")
        return None

def create_test_conversation(contact_id):
    """Create a test conversation"""
    url = f"{CW_URL}/api/v1/accounts/{ACC}/conversations"
    headers = {
        "api_access_token": ADMIN_TOK,
        "Content-Type": "application/json"
    }
    data = {
        "contact_id": contact_id,
        "inbox_id": 1,  # Default inbox
        "custom_attributes": {
            "language": "nl",
            "segment": "new",
            "state": "INIT"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"📨 Conversation creation response: {response.status_code} - {response.text[:200]}")
        if response.status_code == 200:
            conversation = response.json()
            conv_id = conversation.get('id') or conversation.get('payload', {}).get('conversation', {}).get('id')
            if conv_id:
                print(f"✅ Created test conversation: {conv_id}")
                return conv_id
            else:
                print(f"❌ No conversation ID in response: {conversation}")
                return None
        else:
            print(f"❌ Failed to create conversation: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating conversation: {e}")
        return None

def test_send_message(conversation_id, message):
    """Test sending a message using bot token"""
    url = f"{CW_URL}/api/v1/accounts/{ACC}/conversations/{conversation_id}/messages"
    headers = {
        "api_access_token": BOT_TOK,
        "Content-Type": "application/json"
    }
    data = {
        "content": message,
        "message_type": "outgoing"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"✅ Message sent successfully: '{message}'")
            return True
        else:
            print(f"❌ Failed to send message: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

def test_send_quick_replies(conversation_id, text, options):
    """Test sending quick replies"""
    url = f"{CW_URL}/api/v1/accounts/{ACC}/conversations/{conversation_id}/messages"
    headers = {
        "api_access_token": BOT_TOK,
        "Content-Type": "application/json"
    }
    
    quick_replies = []
    for label, value in options:
        quick_replies.append({
            "title": label,
            "payload": value
        })
    
    data = {
        "content": text,
        "message_type": "outgoing",
        "content_attributes": {
            "quick_replies": quick_replies
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"✅ Quick replies sent successfully: '{text}' with {len(options)} options")
            return True
        else:
            print(f"❌ Failed to send quick replies: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending quick replies: {e}")
        return False

def cleanup_test_data(contact_id, conversation_id):
    """Clean up test data"""
    print(f"🧹 Cleaning up test data...")
    
    # Delete conversation
    if conversation_id:
        url = f"{CW_URL}/api/v1/accounts/{ACC}/conversations/{conversation_id}"
        headers = {"api_access_token": ADMIN_TOK}
        try:
            response = requests.delete(url, headers=headers)
            if response.status_code == 200:
                print(f"✅ Deleted conversation {conversation_id}")
            else:
                print(f"⚠️ Could not delete conversation: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Error deleting conversation: {e}")
    
    # Delete contact
    if contact_id:
        url = f"{CW_URL}/api/v1/accounts/{ACC}/contacts/{contact_id}"
        headers = {"api_access_token": ADMIN_TOK}
        try:
            response = requests.delete(url, headers=headers)
            if response.status_code == 200:
                print(f"✅ Deleted contact {contact_id}")
            else:
                print(f"⚠️ Could not delete contact: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Error deleting contact: {e}")

def main():
    """Main test function"""
    print("🧪 Real Conversation Test")
    print("=" * 50)
    
    # Create test contact
    print("👤 Creating test contact...")
    contact_id = create_test_contact()
    if not contact_id:
        print("❌ Cannot proceed without contact")
        return
    
    # Create test conversation
    print("💬 Creating test conversation...")
    conversation_id = create_test_conversation(contact_id)
    if not conversation_id:
        print("❌ Cannot proceed without conversation")
        cleanup_test_data(contact_id, None)
        return
    
    # Wait a moment for conversation to be ready
    print("⏳ Waiting for conversation to be ready...")
    time.sleep(2)
    
    # Test sending messages
    print("📨 Testing message sending...")
    test_send_message(conversation_id, "Hello! This is a test message from the bot.")
    
    time.sleep(1)
    
    # Test sending quick replies
    print("🔘 Testing quick replies...")
    options = [
        ("🇳🇱 Nederlands", "lang_nl"),
        ("🇬🇧 English", "lang_en")
    ]
    test_send_quick_replies(conversation_id, "Choose your language:", options)
    
    time.sleep(1)
    
    # Test another message
    test_send_message(conversation_id, "This is another test message to verify the bot is working.")
    
    print("\n✅ Real conversation test completed!")
    print(f"📊 Contact ID: {contact_id}")
    print(f"📊 Conversation ID: {conversation_id}")
    
    # Ask user if they want to clean up
    response = input("\n🧹 Clean up test data? (y/n): ")
    if response.lower() in ['y', 'yes']:
        cleanup_test_data(contact_id, conversation_id)
    else:
        print(f"💡 Test data preserved. You can manually delete:")
        print(f"   Contact: {contact_id}")
        print(f"   Conversation: {conversation_id}")

if __name__ == "__main__":
    main() 