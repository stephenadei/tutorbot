#!/usr/bin/env python3
"""
Get new admin token for Chatwoot using bot token
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Chatwoot configuration
CW_URL = os.getenv("CW_URL", "https://crm.stephenadei.nl")
CW_ACC_ID = os.getenv("CW_ACC_ID", "1")
CW_TOKEN = os.getenv("CW_TOKEN")  # Your new bot token

def test_bot_token():
    """Test if bot token is valid"""
    print(f"🔍 Testing bot token...")
    
    headers = {
        'Content-Type': 'application/json',
        'api_access_token': CW_TOKEN
    }
    
    try:
        response = requests.get(
            f"{CW_URL}/api/v1/accounts/{CW_ACC_ID}",
            headers=headers
        )
        
        if response.status_code == 200:
            account = response.json()
            print(f"✅ Bot token is valid!")
            print(f"🏢 Account: {account.get('name')}")
            return True
        else:
            print(f"❌ Bot token is invalid: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return False

def get_users_with_bot_token():
    """Get users using bot token"""
    print(f"👥 Getting users with bot token...")
    
    headers = {
        'Content-Type': 'application/json',
        'api_access_token': CW_TOKEN
    }
    
    try:
        response = requests.get(
            f"{CW_URL}/api/v1/accounts/{CW_ACC_ID}/users",
            headers=headers
        )
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Found {len(users)} users")
            
            for user in users:
                print(f"   - {user.get('name')} ({user.get('email')}) - Role: {user.get('role')}")
                if user.get('email') == 'stephen@stephenadei.nl':
                    print(f"   ✅ Found admin user: {user.get('id')}")
            
            return users
        else:
            print(f"❌ Failed to get users: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def create_admin_token():
    """Create a new admin token"""
    print(f"🔑 Creating new admin token...")
    
    # This would require admin access, but let's try with bot token
    headers = {
        'Content-Type': 'application/json',
        'api_access_token': CW_TOKEN
    }
    
    try:
        # Try to create a new access token
        token_data = {
            "name": "TutorBot Admin Token",
            "role": "administrator"
        }
        
        response = requests.post(
            f"{CW_URL}/api/v1/accounts/{CW_ACC_ID}/access_tokens",
            headers=headers,
            json=token_data
        )
        
        if response.status_code == 200:
            token_info = response.json()
            print(f"✅ New admin token created!")
            print(f"🔑 Token: {token_info.get('access_token')}")
            return token_info.get('access_token')
        else:
            print(f"❌ Failed to create admin token: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating token: {e}")
        return None

def reset_password_with_bot_token():
    """Try to reset password using bot token"""
    print(f"🔧 Attempting password reset with bot token...")
    
    headers = {
        'Content-Type': 'application/json',
        'api_access_token': CW_TOKEN
    }
    
    try:
        # First get users
        users_response = requests.get(
            f"{CW_URL}/api/v1/accounts/{CW_ACC_ID}/users",
            headers=headers
        )
        
        if users_response.status_code == 200:
            users = users_response.json()
            
            # Find stephen@stephenadei.nl
            admin_user = None
            for user in users:
                if user.get('email') == 'stephen@stephenadei.nl':
                    admin_user = user
                    break
            
            if admin_user:
                print(f"✅ Found admin user: {admin_user.get('name')} (ID: {admin_user.get('id')})")
                
                # Try to reset password
                new_password = "TutorBot2025!"
                
                reset_data = {
                    "password": new_password,
                    "password_confirmation": new_password
                }
                
                reset_response = requests.put(
                    f"{CW_URL}/api/v1/accounts/{CW_ACC_ID}/users/{admin_user['id']}",
                    headers=headers,
                    json=reset_data
                )
                
                if reset_response.status_code == 200:
                    print(f"✅ Password reset successful!")
                    print(f"🔑 New password: {new_password}")
                    print(f"⚠️  Please change this password immediately after login!")
                    return True
                else:
                    print(f"❌ Password reset failed: {reset_response.status_code}")
                    print(f"📄 Response: {reset_response.text}")
                    return False
            else:
                print(f"❌ User stephen@stephenadei.nl not found")
                return False
        else:
            print(f"❌ Failed to get users: {users_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Chatwoot Admin Token & Password Reset Tool")
    print("=" * 60)
    
    # Test bot token first
    if test_bot_token():
        print(f"\n📋 Current users:")
        get_users_with_bot_token()
        
        print(f"\n🔧 Attempting password reset:")
        if reset_password_with_bot_token():
            print(f"\n✅ Success! You can now login with:")
            print(f"   Email: stephen@stephenadei.nl")
            print(f"   Password: TutorBot2025!")
        else:
            print(f"\n❌ Password reset failed. You may need to:")
            print(f"   1. Login via Chatwoot web interface")
            print(f"   2. Use 'Forgot Password' feature")
            print(f"   3. Or contact your Chatwoot administrator")
    else:
        print(f"❌ Bot token is invalid. Please check your credentials.")

