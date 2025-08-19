#!/usr/bin/env python3
"""
Test Email Integration

This script tests if the Gmail SMTP integration is properly configured
for sending emails from lessons@stephensprivelessen.nl.
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_smtp_connection():
    """Test SMTP connection to Gmail"""
    print("🔍 Testing SMTP Connection...")
    
    # Get SMTP settings
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    if not gmail_user or not gmail_password:
        print("❌ Gmail credentials not configured")
        print("   Set GMAIL_USER and GMAIL_APP_PASSWORD in .env")
        return False
    
    try:
        # Create SMTP connection
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        # Login
        server.login(gmail_user, gmail_password)
        print(f"✅ SMTP connection successful to {smtp_server}:{smtp_port}")
        print(f"✅ Login successful for {gmail_user}")
        
        server.quit()
        return True
        
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        return False

def test_email_sending():
    """Test sending a test email"""
    print("\n🔍 Testing Email Sending...")
    
    # Get SMTP settings
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    if not gmail_user or not gmail_password:
        print("❌ Gmail credentials not configured")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = gmail_user  # Send to self for testing
        msg['Subject'] = "TutorBot Email Test"
        
        body = """
        Dit is een test email van TutorBot.
        
        Als je deze email ontvangt, werkt de email integratie correct!
        
        Best regards,
        TutorBot
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(gmail_user, gmail_password)
        
        text = msg.as_string()
        server.sendmail(gmail_user, gmail_user, text)
        server.quit()
        
        print("✅ Test email sent successfully!")
        print(f"📧 Check your inbox: {gmail_user}")
        return True
        
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

def check_email_config():
    """Check email configuration"""
    print("🔍 Checking Email Configuration...")
    
    config_vars = {
        "GMAIL_USER": "Gmail User",
        "GMAIL_APP_PASSWORD": "Gmail App Password", 
        "SMTP_SERVER": "SMTP Server",
        "SMTP_PORT": "SMTP Port"
    }
    
    all_configured = True
    
    for var, description in config_vars.items():
        value = os.getenv(var)
        if value:
            if "PASSWORD" in var:
                print(f"✅ {description}: {'*' * len(value)}")
            else:
                print(f"✅ {description}: {value}")
        else:
            print(f"❌ {description}: Niet ingesteld")
            all_configured = False
    
    return all_configured

def main():
    """Main test function"""
    print("🚀 Testing Email Integration for lessons@stephensprivelessen.nl")
    print("=" * 70)
    
    # Check configuration
    config_ok = check_email_config()
    
    if not config_ok:
        print("\n⚠️  Email configuration incomplete")
        print("📝 Update your .env file with the required variables:")
        print("   GMAIL_USER=lessons@stephensprivelessen.nl")
        print("   GMAIL_APP_PASSWORD=your_app_password")
        print("   SMTP_SERVER=smtp.gmail.com")
        print("   SMTP_PORT=587")
        return
    
    # Test SMTP connection
    smtp_ok = test_smtp_connection()
    
    # Test email sending
    email_ok = False
    if smtp_ok:
        email_ok = test_email_sending()
    
    print("\n" + "=" * 70)
    print("📊 Email Test Results:")
    print(f"📧 Configuration: {'✅ OK' if config_ok else '❌ FAILED'}")
    print(f"🔗 SMTP Connection: {'✅ OK' if smtp_ok else '❌ FAILED'}")
    print(f"📤 Email Sending: {'✅ OK' if email_ok else '❌ FAILED'}")
    
    if config_ok and smtp_ok and email_ok:
        print("\n🎉 Email integration is working!")
        print("✅ You can send emails from lessons@stephensprivelessen.nl")
        print("✅ SMTP connection is stable")
        print("✅ Test email was sent successfully")
    else:
        print("\n⚠️  Email integration needs attention")
        if not config_ok:
            print("❌ Check your .env configuration")
        if not smtp_ok:
            print("❌ Check your Gmail app password")
            print("❌ Verify 2-factor authentication is enabled")
        if not email_ok:
            print("❌ Check your SMTP settings")

if __name__ == "__main__":
    main()
