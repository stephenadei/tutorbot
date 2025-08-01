#!/usr/bin/env python3
"""
Check Chatwoot Inboxes
Lists available inboxes for conversation creation.
"""

import os
import requests

# Get environment variables
CW_URL = os.getenv("CW_URL", "https://crm.stephenadei.nl")
ACC = os.getenv("CW_ACC_ID", "1")
ADMIN_TOK = os.getenv("CW_ADMIN_TOKEN", "mCNRQJzK4KbVuinP7NszBTug")

def check_inboxes():
    """Check available inboxes"""
    url = f"{CW_URL}/api/v1/accounts/{ACC}/inboxes"
    headers = {
        "api_access_token": ADMIN_TOK,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"📨 Inboxes response: {response.status_code}")
        print(f"📨 Response: {response.text[:500]}")
        
        if response.status_code == 200:
            inboxes = response.json()
            print(f"\n📋 Available inboxes:")
            for inbox in inboxes.get("payload", []):
                print(f"  ID: {inbox.get('id')} | Name: {inbox.get('name')} | Type: {inbox.get('channel_type')}")
        else:
            print(f"❌ Failed to get inboxes")
    except Exception as e:
        print(f"❌ Error getting inboxes: {e}")

if __name__ == "__main__":
    check_inboxes() 