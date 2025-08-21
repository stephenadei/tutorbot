#!/usr/bin/env python3
"""
Wipe all contacts and conversations from Chatwoot
"""

import requests
import os
from datetime import datetime
import time

# Configuration
CW_URL = os.getenv("CW_URL", "https://crm.stephenadei.nl")
ACC_ID = os.getenv("CW_ACC_ID", "1")
ADMIN_TOKEN = os.getenv("CW_ADMIN_TOKEN", "mCNRQJzK4KbVuinP7NszBTug")

if not ADMIN_TOKEN:
    print("❌ CW_ADMIN_TOKEN not set")
    exit(1)

headers = {
    "api_access_token": ADMIN_TOKEN,
    "Content-Type": "application/json"
}

# Configure requests with timeout and retry
session = requests.Session()
session.timeout = 60  # 60 second timeout

def test_connection():
    """Test if we can connect to Chatwoot API"""
    import sys
    auto_mode = "--auto-wipe" in sys.argv
    
    if not auto_mode:
        print("🔗 Testing connection to Chatwoot API...")
    try:
        url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/contacts?per_page=1"
        if not auto_mode:
            print(f"📡 Testing URL: {url}")
        response = session.get(url, headers=headers, timeout=30)
        if not auto_mode:
            print(f"✅ Connection test successful: {response.status_code}")
        if response.status_code == 200:
            return True
        else:
            print(f"❌ API returned error: {response.status_code} - {response.text[:100]}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Connection timeout - server took too long to respond")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error - cannot reach server: {e}")
        return False
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL error - certificate problem: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected connection error: {e}")
        return False

def wipe_contacts():
    """Wipe all contacts and conversations"""
    import sys
    auto_mode = "--auto-wipe" in sys.argv
    
    if not auto_mode:
        print("🧹 Starting complete wipe of contacts and conversations...")
    
    # Test connection first
    if not test_connection():
        print("❌ Cannot connect to Chatwoot API - aborting wipe")
        return
    
    try:
        # Get all contacts
        url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/contacts"
        if not auto_mode:
            print(f"📡 Fetching contacts from: {url}")
        response = session.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to get contacts: {response.status_code} - {response.text}")
            return
        
        contacts = response.json().get("payload", [])
        if not auto_mode:
            print(f"📋 Found {len(contacts)} contacts to delete")
        
        if len(contacts) == 0:
            print("✅ No contacts to delete")
            return
        
        # Delete each contact (this will also delete conversations)
        deleted_count = 0
        deleted_contacts = []  # collect small summary for output
        for i, contact in enumerate(contacts, 1):
            contact_id = contact.get("id")
            contact_name = contact.get("name", "Unknown")
            
            if contact_id:
                if not auto_mode:
                    print(f"🗑️ Deleting contact {i}/{len(contacts)}: {contact_name} (ID: {contact_id})")
                delete_url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/contacts/{contact_id}"
                delete_response = session.delete(delete_url, headers=headers, timeout=30)
                
                if delete_response.status_code == 200:
                    if not auto_mode:
                        print(f"✅ Deleted contact {contact_id}")
                    deleted_count += 1
                    if len(deleted_contacts) < 20:  # cap summary list to avoid huge output
                        deleted_contacts.append({"id": contact_id, "name": contact_name})
                else:
                    print(f"❌ Failed to delete contact {contact_id}: {delete_response.status_code}")
                
                # Small delay to prevent overwhelming the API
                time.sleep(0.5)
        
        # Always print a concise summary (even in auto mode)
        print(f"🎉 Successfully deleted {deleted_count} contacts and their conversations")
        if deleted_contacts:
            print("🧾 Deleted contacts (sample up to 20):")
            for dc in deleted_contacts:
                print(f"   • {dc['name']} (ID: {dc['id']})")
        
        # Also get and delete any remaining conversations
        if not auto_mode:
            print("🔍 Checking for remaining conversations...")
        conv_url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/conversations"
        conv_response = session.get(conv_url, headers=headers, timeout=30)
        
        if conv_response.status_code == 200:
            conversations = conv_response.json().get("payload", [])
            if not auto_mode:
                print(f"📋 Found {len(conversations)} remaining conversations to delete")
            
            for i, conv in enumerate(conversations, 1):
                conv_id = conv.get("id")
                if conv_id:
                    if not auto_mode:
                        print(f"🗑️ Deleting conversation {i}/{len(conversations)}: {conv_id}")
                    delete_conv_url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/conversations/{conv_id}"
                    delete_conv_response = session.delete(delete_conv_url, headers=headers, timeout=30)
                    
                    if delete_conv_response.status_code == 200:
                        if not auto_mode:
                            print(f"✅ Deleted conversation {conv_id}")
                    else:
                        print(f"❌ Failed to delete conversation {conv_id}: {delete_conv_response.status_code}")
                    
                    # Small delay to prevent overwhelming the API
                    time.sleep(0.5)
        else:
            print(f"⚠️ Could not fetch conversations: {conv_response.status_code}")
        
        if not auto_mode:
            print("🎯 Complete wipe finished!")
        
    except KeyboardInterrupt:
        print("\n⏸️ Wipe cancelled by user")
        print("⚠️ Some contacts may have been deleted already")
    except requests.exceptions.Timeout:
        print("❌ Request timeout - server took too long to respond")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - cannot reach server")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    import sys
    
    # Check if called with --auto-wipe flag (from bash script)
    auto_mode = "--auto-wipe" in sys.argv
    
    if not auto_mode:
        print("🗑️  TutorBot - Quick Contact Wipe")
        print("=" * 33)
        print(f"📅 {datetime.now().strftime('%c')}")
        print()
        print("✅ Environment variables configured")
        print(f"🌐 CW_URL: {CW_URL}")
        print(f"📊 CW_ACC_ID: {ACC_ID}")
        print(f"🔑 CW_ADMIN_TOKEN: {ADMIN_TOKEN[:10]}...")
        print()
    
    wipe_contacts() 