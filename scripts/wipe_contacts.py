#!/usr/bin/env python3
"""
Wipe all contacts and conversations from Chatwoot
"""

import requests
import os
from datetime import datetime

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

def wipe_contacts():
    """Wipe all contacts and conversations"""
    print("🧹 Starting complete wipe of contacts and conversations...")
    
    # Get all contacts
    url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/contacts"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get contacts: {response.status_code}")
        return
    
    contacts = response.json().get("payload", [])
    print(f"📋 Found {len(contacts)} contacts to delete")
    
    # Delete each contact (this will also delete conversations)
    deleted_count = 0
    for contact in contacts:
        contact_id = contact.get("id")
        if contact_id:
            delete_url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/contacts/{contact_id}"
            delete_response = requests.delete(delete_url, headers=headers)
            
            if delete_response.status_code == 200:
                print(f"✅ Deleted contact {contact_id}")
                deleted_count += 1
            else:
                print(f"❌ Failed to delete contact {contact_id}: {delete_response.status_code}")
    
    print(f"🎉 Successfully deleted {deleted_count} contacts and their conversations")
    
    # Also get and delete any remaining conversations
    conv_url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/conversations"
    conv_response = requests.get(conv_url, headers=headers)
    
    if conv_response.status_code == 200:
        conversations = conv_response.json().get("payload", [])
        print(f"📋 Found {len(conversations)} remaining conversations to delete")
        
        for conv in conversations:
            conv_id = conv.get("id")
            if conv_id:
                delete_conv_url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/conversations/{conv_id}"
                delete_conv_response = requests.delete(delete_conv_url, headers=headers)
                
                if delete_conv_response.status_code == 200:
                    print(f"✅ Deleted conversation {conv_id}")
                else:
                    print(f"❌ Failed to delete conversation {conv_id}: {delete_conv_response.status_code}")
    
    print("🎯 Complete wipe finished!")

if __name__ == "__main__":
    wipe_contacts() 