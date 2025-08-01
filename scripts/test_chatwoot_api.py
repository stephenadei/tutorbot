#!/usr/bin/env python3
"""
Test Chatwoot API Connection
Tests the connection to Chatwoot and identifies permission issues.
"""

import os
import requests
import json

# Get environment variables
CW_URL = os.getenv("CW_URL", "https://crm.stephenadei.nl")
ACC = os.getenv("CW_ACC_ID", "1")
TOK = os.getenv("CW_TOKEN", "R3vx2s67k7hUpXsLWqDrE6nR")
ADMIN_TOK = os.getenv("CW_ADMIN_TOKEN", "mCNRQJzK4KbVuinP7NszBTug")

def test_api_endpoint(endpoint, token, description):
    """Test a specific API endpoint"""
    url = f"{CW_URL}/api/v1/accounts/{ACC}/{endpoint}"
    headers = {
        "api_access_token": token,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"🔍 {description}:")
        print(f"  URL: {url}")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print(f"  ✅ SUCCESS")
        else:
            print(f"  ❌ FAILED")
        
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"🔍 {description}:")
        print(f"  URL: {url}")
        print(f"  ❌ ERROR: {e}")
        print()
        return False

def test_post_endpoint(endpoint, token, data, description):
    """Test a POST API endpoint"""
    url = f"{CW_URL}/api/v1/accounts/{ACC}/{endpoint}"
    headers = {
        "api_access_token": token,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"🔍 {description}:")
        print(f"  URL: {url}")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        
        if response.status_code in [200, 201]:
            print(f"  ✅ SUCCESS")
        else:
            print(f"  ❌ FAILED")
        
        print()
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"🔍 {description}:")
        print(f"  URL: {url}")
        print(f"  ❌ ERROR: {e}")
        print()
        return False

def main():
    """Main test function"""
    print("🔍 Chatwoot API Connection Test")
    print("=" * 50)
    print(f"CW_URL: {CW_URL}")
    print(f"ACC_ID: {ACC}")
    print(f"BOT_TOKEN: {TOK[:10]}...")
    print(f"ADMIN_TOKEN: {ADMIN_TOK[:10]}...")
    print()
    
    # Test basic connectivity
    print("🌐 Testing basic connectivity...")
    try:
        response = requests.get(f"{CW_URL}/api/v1/accounts/{ACC}")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print("  ✅ Chatwoot is reachable")
        else:
            print("  ❌ Chatwoot is not reachable")
    except Exception as e:
        print(f"  ❌ Connection error: {e}")
    print()
    
    # Test bot token permissions
    print("🤖 Testing bot token permissions...")
    bot_tests = [
        ("conversations", TOK, "List conversations (bot token)"),
        ("contacts", TOK, "List contacts (bot token)"),
        ("custom_attribute_definitions", TOK, "List custom attributes (bot token)"),
    ]
    
    bot_success = 0
    for endpoint, token, desc in bot_tests:
        if test_api_endpoint(endpoint, token, desc):
            bot_success += 1
    
    # Test admin token permissions
    print("👑 Testing admin token permissions...")
    admin_tests = [
        ("conversations", ADMIN_TOK, "List conversations (admin token)"),
        ("contacts", ADMIN_TOK, "List contacts (admin token)"),
        ("custom_attribute_definitions", ADMIN_TOK, "List custom attributes (admin token)"),
        ("labels", ADMIN_TOK, "List labels (admin token)"),
        ("teams", ADMIN_TOK, "List teams (admin token)"),
    ]
    
    admin_success = 0
    for endpoint, token, desc in admin_tests:
        if test_api_endpoint(endpoint, token, desc):
            admin_success += 1
    
    # Test message sending (if we have a conversation)
    print("💬 Testing message sending...")
    try:
        # Try to get a conversation first
        url = f"{CW_URL}/api/v1/accounts/{ACC}/conversations"
        headers = {"api_access_token": ADMIN_TOK}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            conversations = response.json().get("payload", [])
            if conversations:
                conv_id = conversations[0]["id"]
                test_message = {
                    "content": "Test message from API",
                    "message_type": "outgoing"
                }
                test_post_endpoint(f"conversations/{conv_id}/messages", TOK, test_message, f"Send message to conversation {conv_id}")
            else:
                print("  ⚠️ No conversations found to test message sending")
        else:
            print("  ❌ Could not fetch conversations for message testing")
    except Exception as e:
        print(f"  ❌ Message testing error: {e}")
    
    # Summary
    print("📊 Test Summary:")
    print(f"  Bot token tests: {bot_success}/{len(bot_tests)} passed")
    print(f"  Admin token tests: {admin_success}/{len(admin_tests)} passed")
    
    if bot_success < len(bot_tests):
        print("\n⚠️ Bot token has limited permissions. This may cause issues with:")
        print("  • Sending messages")
        print("  • Creating conversations")
        print("  • Accessing contact data")
        print("\n💡 Solutions:")
        print("  1. Check bot token permissions in Chatwoot admin")
        print("  2. Ensure bot has 'conversation_agent' role")
        print("  3. Verify account ID is correct")
    
    if admin_success < len(admin_tests):
        print("\n⚠️ Admin token has limited permissions. This may cause issues with:")
        print("  • Setting contact attributes")
        print("  • Managing labels")
        print("  • Team assignments")
        print("\n💡 Solutions:")
        print("  1. Check admin token permissions in Chatwoot admin")
        print("  2. Ensure admin has 'administrator' role")
        print("  3. Verify account ID is correct")

if __name__ == "__main__":
    main() 