#!/usr/bin/env python3
"""
Check where password reset emails are sent for Chatwoot
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
CW_TOKEN = os.getenv("CW_TOKEN")  # Your bot token

def check_password_reset_endpoint():
    """Check if password reset endpoint exists and what email it uses"""
    print(f"🔍 Checking password reset endpoint...")
    
    try:
        # Try to access the password reset page
        response = requests.get(f"{CW_URL}/auth/forgot_password")
        
        if response.status_code == 200:
            print(f"✅ Password reset page is accessible")
            print(f"📄 Page content preview: {response.text[:200]}...")
        else:
            print(f"❌ Password reset page not accessible: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error accessing password reset page: {e}")

def trigger_password_reset():
    """Trigger a password reset for stephen@stephenadei.nl"""
    print(f"📧 Triggering password reset for stephen@stephenadei.nl...")
    
    try:
        # Try to trigger password reset
        reset_data = {
            "email": "stephen@stephenadei.nl"
        }
        
        response = requests.post(
            f"{CW_URL}/auth/forgot_password",
            json=reset_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print(f"✅ Password reset email sent!")
            print(f"📧 Email sent to: stephen@stephenadei.nl")
            print(f"📄 Response: {response.text}")
        else:
            print(f"❌ Password reset failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error triggering password reset: {e}")

def check_chatwoot_config():
    """Check Chatwoot configuration for email settings"""
    print(f"⚙️ Checking Chatwoot configuration...")
    
    try:
        # Try to get some basic info about the Chatwoot instance
        response = requests.get(f"{CW_URL}/")
        
        if response.status_code == 200:
            print(f"✅ Chatwoot instance is accessible")
            
            # Look for any configuration hints in the HTML
            if "stephen@stephenadei.nl" in response.text:
                print(f"✅ Found email reference in page")
            else:
                print(f"ℹ️ No email reference found in page")
        else:
            print(f"❌ Cannot access Chatwoot instance: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking Chatwoot config: {e}")

def check_email_domains():
    """Check what email domains are configured"""
    print(f"📧 Checking email configuration...")
    
    # Common email domains to check
    email_domains = [
        "stephen@stephenadei.nl",
        "stephen@stephensprivelessen.nl", 
        "admin@stephenadei.nl",
        "admin@stephensprivelessen.nl",
        "info@stephenadei.nl",
        "info@stephensprivelessen.nl"
    ]
    
    for email in email_domains:
        try:
            reset_data = {"email": email}
            response = requests.post(
                f"{CW_URL}/auth/forgot_password",
                json=reset_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print(f"✅ Password reset available for: {email}")
            elif response.status_code == 404:
                print(f"❌ User not found: {email}")
            else:
                print(f"ℹ️ Status {response.status_code} for: {email}")
                
        except Exception as e:
            print(f"❌ Error checking {email}: {e}")

if __name__ == "__main__":
    print("🔧 Chatwoot Password Reset Email Checker")
    print("=" * 50)
    
    check_password_reset_endpoint()
    print()
    
    check_chatwoot_config()
    print()
    
    print("📧 Testing password reset for different email addresses:")
    check_email_domains()
    print()
    
    print("💡 Manual steps to reset password:")
    print("1. Go to: https://crm.stephenadei.nl/auth/forgot_password")
    print("2. Enter your email address")
    print("3. Check your email for reset link")
    print("4. Follow the link to set a new password")

