#!/usr/bin/env python3
"""
Test Chatwoot API connection and credentials
"""

import os
import sys
import requests
from typing import Dict, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.cw_api import ChatwootAPI, _admin_headers, _user_headers

def test_api_credentials():
    """Test if API credentials are working"""
    print("🔍 Testing Chatwoot API credentials...")
    
    # Check environment variables
    cw_url = os.getenv("CW_URL")
    acc_id = os.getenv("CW_ACC_ID")
    admin_token = os.getenv("CW_ADMIN_TOKEN")
    user_token = os.getenv("CW_TOKEN")
    
    print(f"   CW_URL: {cw_url}")
    print(f"   CW_ACC_ID: {acc_id}")
    print(f"   CW_ADMIN_TOKEN: {'***' + admin_token[-4:] if admin_token else 'NOT SET'}")
    print(f"   CW_TOKEN: {'***' + user_token[-4:] if user_token else 'NOT SET'}")
    
    if not all([cw_url, acc_id, admin_token, user_token]):
        print("❌ Missing required environment variables!")
        return False
    
    # Test admin token
    print("\n🔑 Testing admin token...")
    try:
        response = requests.get(
            f"{cw_url}/api/v1/accounts/{acc_id}/conversations",
            headers=_admin_headers(),
            timeout=10,
            verify=False
        )
        if response.status_code == 200:
            data = response.json()
            conversation_count = len(data.get("data", {}).get("payload", []))
            print(f"✅ Admin token works! Found {conversation_count} conversations")
        else:
            print(f"❌ Admin token failed: {response.status_code} - {response.text[:100]}")
            return False
    except Exception as e:
        print(f"❌ Admin token test failed: {e}")
        return False
    
    # Test user token
    print("\n🔑 Testing user token...")
    try:
        response = requests.get(
            f"{cw_url}/api/v1/accounts/{acc_id}/conversations",
            headers=_user_headers(),
            timeout=10,
            verify=False
        )
        if response.status_code == 200:
            print("✅ User token works!")
        else:
            print(f"❌ User token failed: {response.status_code} - {response.text[:100]}")
            return False
    except Exception as e:
        print(f"❌ User token test failed: {e}")
        return False
    
    # Test specific conversation (if any exist)
    print("\n🔍 Testing specific conversation access...")
    try:
        response = requests.get(
            f"{cw_url}/api/v1/accounts/{acc_id}/conversations",
            headers=_admin_headers(),
            timeout=10,
            verify=False
        )
        if response.status_code == 200:
            data = response.json()
            conversations = data.get("data", {}).get("payload", [])
            
            if conversations:
                # Test first conversation
                conv_id = conversations[0]["id"]
                print(f"   Testing conversation {conv_id}...")
                
                response = requests.get(
                    f"{cw_url}/api/v1/accounts/{acc_id}/conversations/{conv_id}",
                    headers=_admin_headers(),
                    timeout=10,
                    verify=False
                )
                
                if response.status_code == 200:
                    conv_data = response.json()
                    print(f"✅ Conversation {conv_id} accessible")
                    
                    # Test setting custom attributes
                    test_attrs = {"test_api": "working"}
                    response = requests.post(
                        f"{cw_url}/api/v1/accounts/{acc_id}/conversations/{conv_id}/custom_attributes",
                        headers=_admin_headers(),
                        json={"custom_attributes": test_attrs},
                        timeout=10,
                        verify=False
                    )
                    
                    if response.status_code == 200:
                        print(f"✅ Custom attributes can be set on conversation {conv_id}")
                    else:
                        print(f"❌ Failed to set custom attributes: {response.status_code}")
                        return False
                else:
                    print(f"❌ Failed to access conversation {conv_id}: {response.status_code}")
                    return False
            else:
                print("⚠️ No conversations found to test")
        else:
            print(f"❌ Failed to get conversations: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Conversation test failed: {e}")
        return False
    
    print("\n✅ All API tests passed!")
    return True

def test_cw_api_functions():
    """Test the ChatwootAPI class functions"""
    print("\n🧪 Testing ChatwootAPI class functions...")
    
    # Test get_conversation
    print("   Testing get_conversation...")
    try:
        response = requests.get(
            f"{os.getenv('CW_URL')}/api/v1/accounts/{os.getenv('CW_ACC_ID')}/conversations",
            headers=_admin_headers(),
            timeout=10,
            verify=False
        )
        if response.status_code == 200:
            data = response.json()
            conversations = data.get("data", {}).get("payload", [])
            
            if conversations:
                conv_id = conversations[0]["id"]
                conv = ChatwootAPI.get_conversation(conv_id)
                if conv:
                    print(f"✅ get_conversation({conv_id}) works")
                else:
                    print(f"❌ get_conversation({conv_id}) failed")
                    return False
            else:
                print("⚠️ No conversations to test get_conversation")
        else:
            print(f"❌ Failed to get conversations list: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ get_conversation test failed: {e}")
        return False
    
    # Test get_conv_attrs
    print("   Testing get_conv_attrs...")
    try:
        response = requests.get(
            f"{os.getenv('CW_URL')}/api/v1/accounts/{os.getenv('CW_ACC_ID')}/conversations",
            headers=_admin_headers(),
            timeout=10,
            verify=False
        )
        if response.status_code == 200:
            data = response.json()
            conversations = data.get("data", {}).get("payload", [])
            
            if conversations:
                conv_id = conversations[0]["id"]
                attrs = ChatwootAPI.get_conv_attrs(conv_id)
                print(f"✅ get_conv_attrs({conv_id}) works - found {len(attrs)} attributes")
            else:
                print("⚠️ No conversations to test get_conv_attrs")
        else:
            print(f"❌ Failed to get conversations list: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ get_conv_attrs test failed: {e}")
        return False
    
    print("✅ All ChatwootAPI function tests passed!")
    return True

def main():
    """Main test function"""
    print("🚀 Starting Chatwoot API connection tests...\n")
    
    # Test 1: API credentials
    if not test_api_credentials():
        print("\n❌ API credentials test failed!")
        return False
    
    # Test 2: ChatwootAPI functions
    if not test_cw_api_functions():
        print("\n❌ ChatwootAPI functions test failed!")
        return False
    
    print("\n🎉 All tests passed! API connection is working correctly.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 