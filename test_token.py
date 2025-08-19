#!/usr/bin/env python3
"""
Test bot token with Chatwoot API endpoints
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
CW_TOKEN = os.getenv("CW_TOKEN", "uDSMCbD1EH4cBBDbSgj35WKS")

def test_token_with_endpoint(endpoint, description):
    """Test token with specific endpoint"""
    print(f"🔍 Testing: {description}")
    print(f"   URL: {CW_URL}{endpoint}")
    
    headers = {
        'Content-Type': 'application/json',
        'api_access_token': CW_TOKEN
    }
    
    try:
        response = requests.get(f"{CW_URL}{endpoint}", headers=headers)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success!")
            
            if isinstance(data, dict):
                print(f"   Data: {json.dumps(data, indent=2)}")
            elif isinstance(data, list):
                print(f"   Items: {len(data)}")
                if data:
                    print(f"   First item: {json.dumps(data[0], indent=2)}")
            
            return True
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_all_endpoints():
    """Test token with all relevant endpoints"""
    print("🔑 Bot Token Test Suite")
    print("=" * 40)
    
    endpoints = [
        ("/api/v1/accounts/1", "Account Info"),
        ("/api/v1/accounts/1/inboxes", "Inboxes"),
        ("/api/v1/accounts/1/conversations", "Conversations"),
        ("/api/v1/accounts/1/contacts", "Contacts"),
        ("/api/v1/accounts/1/agents", "Agents"),
        ("/api/v1/accounts/1/webhooks", "Webhooks"),
        ("/api/v1/accounts/1/bots", "Bots"),
    ]
    
    results = {}
    
    for endpoint, description in endpoints:
        print(f"\n{'-' * 20}")
        success = test_token_with_endpoint(endpoint, description)
        results[description] = success
    
    print(f"\n{'=' * 40}")
    print("📊 Test Results Summary:")
    
    for description, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {description}")
    
    # Summary
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == 0:
        print("❌ Token has no API access - check if it's a valid bot token")
    elif passed < total:
        print("⚠️ Token has limited access - some endpoints restricted")
    else:
        print("✅ Token has full API access")

if __name__ == "__main__":
    test_all_endpoints()

