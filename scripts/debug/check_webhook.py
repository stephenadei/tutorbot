#!/usr/bin/env python3
"""
Check and configure Chatwoot webhook for WhatsApp integration
"""

import os
import sys
import requests
import json
from typing import Dict, Any

def ensure_project_root():
    """Ensure we're running from the project root directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    required_files = [
        "main.py",
        "requirements.txt", 
        "config/contact_attributes.yaml"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(project_root, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Error: Script must be run from the project root directory!")
        print(f"   Current directory: {os.getcwd()}")
        print(f"   Expected project root: {project_root}")
        print(f"   Missing files: {', '.join(missing_files)}")
        print(f"\n💡 Solution: Run from the project root:")
        print(f"   cd {project_root}")
        print(f"   python3 scripts/check_webhook.py")
        sys.exit(1)
    
    if os.getcwd() != project_root:
        print(f"🔄 Changing to project root: {project_root}")
        os.chdir(project_root)
    
    return project_root

# Ensure we're in the right directory before importing anything else
PROJECT_ROOT = ensure_project_root()

# Configuration
CW_URL = os.getenv("CW_URL", "https://crm.stephenadei.nl")
ACC_ID = os.getenv("CW_ACC_ID")
ADMIN_TOKEN = os.getenv("CW_ADMIN_TOKEN")

def get_webhooks():
    """Get current webhooks from Chatwoot"""
    url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/webhooks"
    headers = {"api_access_token": ADMIN_TOKEN}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting webhooks: {e}")
        return None

def create_webhook():
    """Create webhook for TutorBot"""
    url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/webhooks"
    headers = {
        "api_access_token": ADMIN_TOKEN,
        "Content-Type": "application/json"
    }
    
    # Get server IP/domain
    webhook_url = "http://localhost:8000/cw"  # Default local URL
    
    # Try to get public IP
    try:
        ip_response = requests.get("https://api.ipify.org", timeout=5)
        if ip_response.status_code == 200:
            public_ip = ip_response.text
            webhook_url = f"http://{public_ip}:8000/cw"
            print(f"🌐 Using public IP: {public_ip}")
    except:
        print("⚠️ Could not get public IP, using localhost")
    
    data = {
        "url": webhook_url,
        "subscriptions": ["message_created", "conversation_created"],
        "status": "enabled"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating webhook: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        return None

def update_webhook(webhook_id, webhook_url):
    """Update existing webhook"""
    url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/webhooks/{webhook_id}"
    headers = {
        "api_access_token": ADMIN_TOKEN,
        "Content-Type": "application/json"
    }
    
    data = {
        "url": webhook_url,
        "subscriptions": ["message_created", "conversation_created"],
        "status": "enabled"
    }
    
    try:
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error updating webhook: {e}")
        return None

def test_webhook():
    """Test webhook by sending a test message"""
    print("\n🧪 Testing webhook...")
    
    # Test the webhook endpoint
    test_data = {
        "event": "message_created",
        "message_type": "incoming",
        "conversation": {"id": 999},
        "contact": {"id": 888},
        "content": "TEST MESSAGE - Webhook test",
        "id": "test_123"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/cw",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Webhook test successful!")
            print(f"   Response: {response.text}")
        else:
            print(f"❌ Webhook test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Webhook test error: {e}")

def main():
    """Main function"""
    print("🔍 Checking Chatwoot webhook configuration...")
    print(f"   Chatwoot URL: {CW_URL}")
    print(f"   Account ID: {ACC_ID}")
    print(f"   Admin Token: {'*' * 10 if ADMIN_TOKEN else 'NOT SET'}")
    
    if not all([CW_URL, ACC_ID, ADMIN_TOKEN]):
        print("❌ Missing required environment variables!")
        print("   Please set: CW_URL, CW_ACC_ID, CW_ADMIN_TOKEN")
        return
    
    # Get current webhooks
    print("\n📋 Current webhooks:")
    webhooks = get_webhooks()
    
    if webhooks is None:
        print("❌ Could not retrieve webhooks")
        return
    
    if not webhooks:
        print("   No webhooks found")
        print("\n➕ Creating new webhook...")
        new_webhook = create_webhook()
        if new_webhook:
            print("✅ Webhook created successfully!")
            print(f"   ID: {new_webhook.get('id')}")
            print(f"   URL: {new_webhook.get('url')}")
        else:
            print("❌ Failed to create webhook")
    else:
        print(f"   Found {len(webhooks)} webhook(s):")
        for webhook in webhooks:
            print(f"   - ID: {webhook.get('id')}")
            print(f"     URL: {webhook.get('url')}")
            print(f"     Status: {webhook.get('status')}")
            print(f"     Subscriptions: {webhook.get('subscriptions')}")
            
            # Check if this is our TutorBot webhook
            if "8000/cw" in webhook.get('url', ''):
                print("   ✅ This appears to be the TutorBot webhook")
                
                # Check if URL needs updating
                if "localhost" in webhook.get('url', ''):
                    print("   ⚠️ Webhook is using localhost - may not work from external sources")
                    
                    # Try to update with public IP
                    try:
                        ip_response = requests.get("https://api.ipify.org", timeout=5)
                        if ip_response.status_code == 200:
                            public_ip = ip_response.text
                            new_url = f"http://{public_ip}:8000/cw"
                            print(f"   🔄 Updating webhook URL to: {new_url}")
                            
                            updated = update_webhook(webhook['id'], new_url)
                            if updated:
                                print("   ✅ Webhook updated successfully!")
                            else:
                                print("   ❌ Failed to update webhook")
                    except:
                        print("   ⚠️ Could not get public IP for update")
    
    # Test the webhook
    test_webhook()
    
    print("\n📝 Next steps:")
    print("   1. Make sure TutorBot is running: sudo gunicorn --bind 0.0.0.0:8000 main:app")
    print("   2. Send a WhatsApp message to test")
    print("   3. Check logs for webhook activity")

if __name__ == "__main__":
    main()
