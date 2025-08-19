#!/usr/bin/env python3
"""
Test Real Email Service

This script tests the real email service using Google Workspace SMTP
for lessons@stephensprivelessen.nl
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_configuration():
    """Test if email configuration is properly set up"""
    print("🔍 Testing Email Configuration...")
    
    # Check environment variables
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    print(f"📧 Gmail User: {gmail_user or 'NOT SET'}")
    print(f"🔑 Gmail App Password: {'SET' if gmail_password else 'NOT SET'}")
    
    if not gmail_user:
        print("❌ GMAIL_USER not set in .env")
        print("   Add: GMAIL_USER=lessons@stephensprivelessen.nl")
        return False
    
    if not gmail_password:
        print("❌ GMAIL_APP_PASSWORD not set in .env")
        print("   Add: GMAIL_APP_PASSWORD=your_app_password")
        return False
    
    print("✅ Email configuration looks good!")
    return True

def test_real_email_service():
    """Test the real email service"""
    print("\n🧪 Testing Real Email Service...")
    
    try:
        from real_email_service import RealEmailService
        
        service = RealEmailService()
        
        # Test with a real email address (replace with your test email)
        test_email = input("📧 Enter test email address: ").strip()
        
        if not test_email:
            print("❌ No email address provided")
            return False
        
        print(f"📤 Sending test email to: {test_email}")
        
        # Send test email
        result = service.send_email(
            to_email=test_email,
            subject="Test Email - TutorBot Real Email Service",
            body="""
Dit is een test email van TutorBot Real Email Service.

Als je deze email ontvangt, werkt de Google Workspace SMTP integratie correct!

Best regards,
TutorBot
            """,
            from_name="TutorBot Test"
        )
        
        if result:
            print("✅ Test email sent successfully!")
            print(f"📧 Check your inbox: {test_email}")
            return True
        else:
            print("❌ Test email failed!")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_trial_confirmation():
    """Test trial confirmation email"""
    print("\n🧪 Testing Trial Confirmation Email...")
    
    try:
        from real_email_service import RealEmailService
        
        service = RealEmailService()
        
        # Test with a real email address
        test_email = input("📧 Enter test email address for trial confirmation: ").strip()
        
        if not test_email:
            print("❌ No email address provided")
            return False
        
        print(f"📤 Sending trial confirmation to: {test_email}")
        
        # Send trial confirmation
        result = service.send_trial_confirmation(
            to_email=test_email,
            student_name="Test Student",
            lesson_date="Maandag 25 augustus 2025",
            lesson_time="14:00 - 15:00"
        )
        
        if result:
            print("✅ Trial confirmation sent successfully!")
            return True
        else:
            print("❌ Trial confirmation failed!")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 TutorBot Real Email Service Test")
    print("=" * 50)
    
    # Test configuration
    if not test_email_configuration():
        print("\n❌ Configuration test failed!")
        print("   Please set up GMAIL_USER and GMAIL_APP_PASSWORD in .env")
        return False
    
    # Test basic email
    if not test_real_email_service():
        print("\n❌ Basic email test failed!")
        return False
    
    # Test trial confirmation
    if not test_trial_confirmation():
        print("\n❌ Trial confirmation test failed!")
        return False
    
    print("\n🎉 All tests passed! Email service is working correctly!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
