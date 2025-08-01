#!/usr/bin/env python3
"""
Cleanup All Data
Deletes all contacts and conversations from Chatwoot.
"""

import os
import requests
import time

# Get environment variables
CW_URL = os.getenv("CW_URL", "https://crm.stephenadei.nl")
ACC = os.getenv("CW_ACC_ID", "1")
ADMIN_TOK = os.getenv("CW_ADMIN_TOKEN", "mCNRQJzK4KbVuinP7NszBTug")

def delete_all_conversations():
    """Delete all conversations"""
    print("🗑️ Deleting all conversations...")
    
    # Get all conversations
    url = f"{CW_URL}/api/v1/accounts/{ACC}/conversations"
    headers = {"api_access_token": ADMIN_TOK}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            conversations = response.json().get("payload", [])
            print(f"📋 Found {len(conversations)} conversations")
            
            for conv in conversations:
                conv_id = conv.get("id")
                if conv_id:
                    delete_url = f"{CW_URL}/api/v1/accounts/{ACC}/conversations/{conv_id}"
                    delete_response = requests.delete(delete_url, headers=headers)
                    if delete_response.status_code == 200:
                        print(f"✅ Deleted conversation {conv_id}")
                    else:
                        print(f"❌ Failed to delete conversation {conv_id}: {delete_response.status_code}")
                    time.sleep(0.5)  # Small delay to avoid rate limiting
        else:
            print(f"❌ Failed to get conversations: {response.status_code}")
    except Exception as e:
        print(f"❌ Error deleting conversations: {e}")

def delete_all_contacts():
    """Delete all contacts"""
    print("🗑️ Deleting all contacts...")
    
    # Get all contacts
    url = f"{CW_URL}/api/v1/accounts/{ACC}/contacts"
    headers = {"api_access_token": ADMIN_TOK}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            contacts = response.json().get("payload", [])
            print(f"📋 Found {len(contacts)} contacts")
            
            for contact in contacts:
                contact_id = contact.get("id")
                if contact_id:
                    delete_url = f"{CW_URL}/api/v1/accounts/{ACC}/contacts/{contact_id}"
                    delete_response = requests.delete(delete_url, headers=headers)
                    if delete_response.status_code == 200:
                        print(f"✅ Deleted contact {contact_id}")
                    else:
                        print(f"❌ Failed to delete contact {contact_id}: {delete_response.status_code}")
                    time.sleep(0.5)  # Small delay to avoid rate limiting
        else:
            print(f"❌ Failed to get contacts: {response.status_code}")
    except Exception as e:
        print(f"❌ Error deleting contacts: {e}")

def verify_cleanup():
    """Verify that all data is deleted"""
    print("🔍 Verifying cleanup...")
    
    # Check conversations
    conv_url = f"{CW_URL}/api/v1/accounts/{ACC}/conversations"
    headers = {"api_access_token": ADMIN_TOK}
    
    try:
        conv_response = requests.get(conv_url, headers=headers)
        if conv_response.status_code == 200:
            conversations = conv_response.json().get("payload", [])
            print(f"📋 Remaining conversations: {len(conversations)}")
        
        # Check contacts
        contact_url = f"{CW_URL}/api/v1/accounts/{ACC}/contacts"
        contact_response = requests.get(contact_url, headers=headers)
        if contact_response.status_code == 200:
            contacts = contact_response.json().get("payload", [])
            print(f"📋 Remaining contacts: {len(contacts)}")
            
        if len(conversations) == 0 and len(contacts) == 0:
            print("✅ Cleanup successful - all data deleted!")
        else:
            print("⚠️ Some data remains - cleanup may be incomplete")
            
    except Exception as e:
        print(f"❌ Error verifying cleanup: {e}")

def main():
    """Main cleanup function"""
    print("🧹 Chatwoot Data Cleanup")
    print("=" * 50)
    
    # Confirm before proceeding
    response = input("⚠️ This will delete ALL contacts and conversations. Continue? (y/n): ")
    if response.lower() not in ['y', 'yes']:
        print("❌ Cleanup cancelled")
        return
    
    # Delete conversations first (they depend on contacts)
    delete_all_conversations()
    
    # Then delete contacts
    delete_all_contacts()
    
    # Verify cleanup
    verify_cleanup()
    
    print("\n🎯 Cleanup completed! You can now start fresh.")

if __name__ == "__main__":
    main() 