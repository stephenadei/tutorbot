#!/usr/bin/env python3
"""
Simple Email Test

This script tests the email configuration and basic functionality
"""

import os
import sys

def test_email_configuration():
    """Test if email configuration is properly set up"""
    print("🔍 Testing Email Configuration...")
    
    # Check environment variables
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    print(f"📧 Gmail User: {gmail_user or 'NOT SET'}")
    print(f"🔑 Gmail App Password: {'SET' if gmail_password else 'NOT SET'}")
    
    if not gmail_user:
        print("❌ GMAIL_USER not set in environment")
        return False
    
    if not gmail_password:
        print("❌ GMAIL_APP_PASSWORD not set in environment")
        return False
    
    print("✅ Email configuration looks good!")
    return True

def test_temp_email_service():
    """Test the temp email service"""
    print("\n🧪 Testing Temp Email Service...")
    
    try:
        from temp_email_service import TempEmailService
        
        service = TempEmailService()
        
        # Test email logging
        result = service.send_email(
            to_email="test@example.com",
            subject="Test Email - Temp Service",
            body="Dit is een test email van de temp service.",
            from_name="TutorBot Test"
        )
        
        if result:
            print("✅ Temp email service test successful!")
            print("📝 Email logged to email_log.txt")
            return True
        else:
            print("❌ Temp email service test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Temp email service test failed: {e}")
        return False

def test_real_email_service_creation():
    """Test creating the real email service"""
    print("\n🧪 Testing Real Email Service Creation...")
    
    try:
        from real_email_service import RealEmailService
        
        service = RealEmailService()
        
        print(f"✅ Real email service created successfully!")
        print(f"📧 From email: {service.from_email}")
        print(f"🔧 SMTP Server: {service.smtp_server}:{service.smtp_port}")
        print(f"👤 Gmail User: {service.gmail_user}")
        print(f"🔑 Using temp service: {service.use_temp_service}")
        
        return True
        
    except Exception as e:
        print(f"❌ Real email service creation failed: {e}")
        return False

def test_real_email_sending():
    """Test sending a real email"""
    print("\n🧪 Testing Real Email Sending...")
    
    try:
        from real_email_service import RealEmailService
        
        service = RealEmailService()
        
        # Test sending a simple email
        result = service.send_email(
            to_email="test@stephenadei.nl",
            subject="Test Email - Real Service",
            body="Dit is een test email van de real email service.",
            from_name="TutorBot Test"
        )
        
        if result:
            print("✅ Real email sent successfully!")
            print("📧 Check test@stephenadei.nl for the email")
            return True
        else:
            print("❌ Real email sending failed!")
            return False
            
    except Exception as e:
        print(f"❌ Real email sending failed: {e}")
        return False

def test_trial_confirmation_email():
    """Test sending a trial confirmation email"""
    print("\n🧪 Testing Trial Confirmation Email...")
    
    try:
        from real_email_service import RealEmailService
        
        service = RealEmailService()
        
        # Test sending a trial confirmation
        result = service.send_trial_confirmation(
            to_email="test@stephenadei.nl",
            student_name="Test Student",
            lesson_date="2024-01-15",
            lesson_time="14:00"
        )
        
        if result:
            print("✅ Trial confirmation email sent successfully!")
            print("📧 Check test@stephenadei.nl for the trial confirmation")
            return True
        else:
            print("❌ Trial confirmation email failed!")
            return False
            
    except Exception as e:
        print(f"❌ Trial confirmation email failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Simple Email Service Test")
    print("=" * 40)
    
    # Test configuration
    if not test_email_configuration():
        print("\n❌ Configuration test failed!")
        return False
    
    # Test temp email service
    if not test_temp_email_service():
        print("\n❌ Temp email service test failed!")
        return False
    
    # Test real email service creation
    if not test_real_email_service_creation():
        print("\n❌ Real email service creation failed!")
        return False
    
    print("\n🎉 All basic tests passed!")
    print("📧 Email service is ready to use!")
    
    # Ask user if they want to test real email sending
    print("\n" + "=" * 40)
    print("🔧 Advanced Email Testing")
    print("=" * 40)
    
    try:
        response = input("Do you want to test real email sending? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            print("\n📧 Testing Real Email Sending...")
            if test_real_email_sending():
                print("\n✅ Real email test successful!")
                
                response2 = input("Do you want to test trial confirmation email? (y/n): ").lower().strip()
                if response2 in ['y', 'yes']:
                    if test_trial_confirmation_email():
                        print("\n✅ Trial confirmation test successful!")
                    else:
                        print("\n❌ Trial confirmation test failed!")
            else:
                print("\n❌ Real email test failed!")
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
