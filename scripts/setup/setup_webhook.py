#!/usr/bin/env python3
"""
Setup Chatwoot webhook for WhatsApp integration
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
        print(f"   python3 scripts/setup_webhook.py")
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

def get_public_ip():
    """Get public IP address"""
    try:
        response = requests.get("https://api.ipify.org", timeout=5)
        if response.status_code == 200:
            return response.text
    except:
        pass
    
    # Fallback: try other IP services
    try:
        response = requests.get("https://ifconfig.me", timeout=5)
        if response.status_code == 200:
            return response.text
    except:
        pass
    
    return None

def create_webhook():
    """Create webhook for TutorBot"""
    print("🔧 Setting up Chatwoot webhook...")
    
    # Get public IP
    public_ip = get_public_ip()
    if public_ip:
        webhook_url = f"http://{public_ip}:8000/cw"
        print(f"🌐 Using public IP: {public_ip}")
        print(f"🔗 Webhook URL: {webhook_url}")
    else:
        print("⚠️ Could not get public IP")
        print("💡 You may need to manually configure the webhook in Chatwoot")
        print("   Webhook URL should be: http://YOUR_SERVER_IP:8000/cw")
        return False
    
    # Test if the webhook endpoint is reachable
    print("🧪 Testing webhook endpoint...")
    try:
        test_response = requests.get(f"http://{public_ip}:8000/", timeout=5)
        print(f"✅ Server is reachable (status: {test_response.status_code})")
    except:
        print("❌ Server is not reachable from external sources")
        print("💡 This could be due to:")
        print("   - Firewall blocking port 8000")
        print("   - Server not accessible from internet")
        print("   - TutorBot not running")
        return False
    
    # Create webhook via Chatwoot API
    url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/webhooks"
    headers = {
        "api_access_token": ADMIN_TOKEN,
        "Content-Type": "application/json"
    }
    
    data = {
        "url": webhook_url,
        "subscriptions": ["message_created", "conversation_created"],
        "status": "enabled"
    }
    
    print(f"📡 Creating webhook in Chatwoot...")
    print(f"   URL: {url}")
    print(f"   Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"   Response status: {response.status_code}")
        print(f"   Response body: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            webhook_data = response.json()
            print("✅ Webhook created successfully!")
            print(f"   ID: {webhook_data.get('id')}")
            print(f"   URL: {webhook_data.get('url')}")
            print(f"   Status: {webhook_data.get('status')}")
            return True
        else:
            print("❌ Failed to create webhook")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating webhook: {e}")
        return False

def test_webhook_manual():
    """Provide manual testing instructions"""
    print("\n📋 Manual Webhook Setup Instructions:")
    print("=" * 50)
    print("1. Open Chatwoot admin panel:")
    print(f"   {CW_URL}/app/admin")
    print()
    print("2. Go to Settings > Integrations > Webhooks")
    print()
    print("3. Create a new webhook with these settings:")
    print("   - URL: http://YOUR_SERVER_IP:8000/cw")
    print("   - Subscriptions: message_created, conversation_created")
    print("   - Status: Enabled")
    print()
    print("4. Replace YOUR_SERVER_IP with your actual server IP")
    print("   Current server IP: " + (get_public_ip() or "UNKNOWN"))
    print()
    print("5. Test the webhook by sending a WhatsApp message")
    print()
    print("6. Check TutorBot logs for incoming messages")

def main():
    """Main function"""
    print("🔍 Setting up Chatwoot webhook for WhatsApp integration...")
    print(f"   Chatwoot URL: {CW_URL}")
    print(f"   Account ID: {ACC_ID}")
    print(f"   Admin Token: {'*' * 10 if ADMIN_TOKEN else 'NOT SET'}")
    
    if not all([CW_URL, ACC_ID, ADMIN_TOKEN]):
        print("❌ Missing required environment variables!")
        print("   Please set: CW_URL, CW_ACC_ID, CW_ADMIN_TOKEN")
        print("\n💡 You can set them manually:")
        print("   export CW_URL='https://crm.stephenadei.nl'")
        print("   export CW_ACC_ID='1'")
        print("   export CW_ADMIN_TOKEN='your_token_here'")
        return
    
    # Try to create webhook automatically
    success = create_webhook()
    
    if not success:
        print("\n🔄 Automatic setup failed, showing manual instructions...")
        test_webhook_manual()
    
    print("\n📝 Next steps:")
    print("   1. Make sure TutorBot is running:")
    print("      sudo gunicorn --bind 0.0.0.0:8000 main:app")
    print("   2. Send a WhatsApp message to test")
    print("   3. Check logs for webhook activity")
    print("   4. If no messages appear, check webhook configuration in Chatwoot")

if __name__ == "__main__":
    main()
