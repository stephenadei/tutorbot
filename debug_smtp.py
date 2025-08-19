#!/usr/bin/env python3
"""
Debug SMTP Connection

This script tests the SMTP connection and email sending with detailed debugging
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_smtp_connection():
    """Test SMTP connection with detailed debugging"""
    print("🔍 Testing SMTP Connection...")
    
    # Get credentials
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    print(f"📧 Gmail User: {gmail_user}")
    print(f"🔑 Password: {'SET' if gmail_password else 'NOT SET'}")
    
    if not gmail_user or not gmail_password:
        print("❌ Missing credentials")
        return False
    
    try:
        # Create SMTP connection
        print("🔌 Creating SMTP connection...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        
        # Enable debug output
        server.set_debuglevel(1)
        
        print("🔐 Starting TLS...")
        server.starttls(context=ssl.create_default_context())
        
        print("🔑 Logging in...")
        server.login(gmail_user, gmail_password)
        
        print("✅ SMTP connection successful!")
        
        # Test sending a simple email
        print("📧 Testing email sending...")
        
        msg = MIMEMultipart()
        msg['From'] = f"Debug Test <{gmail_user}>"
        msg['To'] = "stephenadei@gmail.com"
        msg['Subject'] = "SMTP Debug Test"
        
        body = "This is a debug test email to verify SMTP functionality."
        msg.attach(MIMEText(body, 'plain'))
        
        text = msg.as_string()
        print("📤 Sending email...")
        server.sendmail(gmail_user, "stephenadei@gmail.com", text)
        
        print("✅ Email sent successfully!")
        
        # Close connection
        server.quit()
        print("🔌 SMTP connection closed")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP Authentication Error: {e}")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        print(f"❌ SMTP Recipients Refused: {e}")
        return False
    except smtplib.SMTPSenderRefused as e:
        print(f"❌ SMTP Sender Refused: {e}")
        return False
    except smtplib.SMTPDataError as e:
        print(f"❌ SMTP Data Error: {e}")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"❌ SMTP Connect Error: {e}")
        return False
    except smtplib.SMTPHeloError as e:
        print(f"❌ SMTP Helo Error: {e}")
        return False
    except smtplib.SMTPNotSupportedError as e:
        print(f"❌ SMTP Not Supported Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_real_email_service():
    """Test the real email service with debugging"""
    print("\n🧪 Testing Real Email Service...")
    
    try:
        from real_email_service import RealEmailService
        
        service = RealEmailService()
        print(f"✅ Service created: {service}")
        print(f"📧 From email: {service.from_email}")
        print(f"🔧 SMTP Server: {service.smtp_server}:{service.smtp_port}")
        print(f"👤 Gmail User: {service.gmail_user}")
        print(f"🔑 Using temp service: {service.use_temp_service}")
        
        if service.use_temp_service:
            print("⚠️ Service is using temp service, not real SMTP")
            return False
        
        # Test sending email
        result = service.send_email(
            to_email="stephenadei@gmail.com",
            subject="Real Email Service Test",
            body="This is a test from the real email service.",
            from_name="Real Service Test"
        )
        
        print(f"📤 Email result: {result}")
        return result
        
    except Exception as e:
        print(f"❌ Real email service test failed: {e}")
        return False

def main():
    """Main debug function"""
    print("🚀 SMTP Debug Test")
    print("=" * 50)
    
    # Test direct SMTP connection
    smtp_success = test_smtp_connection()
    
    # Test real email service
    service_success = test_real_email_service()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"SMTP Connection: {'✅ PASS' if smtp_success else '❌ FAIL'}")
    print(f"Real Email Service: {'✅ PASS' if service_success else '❌ FAIL'}")
    
    if smtp_success and service_success:
        print("\n🎉 All tests passed! Email should be working.")
        print("📧 Check stephenadei@gmail.com for test emails")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
    
    return smtp_success and service_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
