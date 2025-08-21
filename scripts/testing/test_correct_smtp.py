#!/usr/bin/env python3
"""
Test Correct SMTP Configuration
"""

import smtplib
import ssl
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_correct_smtp():
    """Test SMTP with correct configuration"""
    print("🔍 Testing SMTP with Correct Configuration...")
    
    # Get credentials
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    print(f"📧 User: {gmail_user}")
    print(f"🔑 Password: {gmail_password[:4]}...{gmail_password[-4:] if gmail_password else 'None'}")
    print()
    
    print("🔧 SMTP Configuration:")
    print("   Server: smtp.gmail.com")
    print("   Port: 587")
    print("   Authentication: plain")
    print("   StartTLS: enabled")
    print("   SSL Verification: peer")
    print()
    
    try:
        # Create SMTP connection with correct settings
        print("🔗 Connecting to Gmail SMTP...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        
        # Enable StartTLS
        print("🔐 Starting TLS...")
        server.starttls(context=ssl.create_default_context())
        
        # Login with plain authentication
        print("🔑 Attempting login...")
        server.login(gmail_user, gmail_password)
        
        print("✅ Login successful!")
        
        # Send test email
        print("📤 Sending test email...")
        message = """Subject: Test Email van TutorBot

Dit is een test email van TutorBot.

Als je deze email ontvangt, werkt de email integratie correct!

Best regards,
TutorBot"""
        
        server.sendmail(gmail_user, gmail_user, message)
        
        print("✅ Test email sent successfully!")
        print(f"📧 Check je inbox: {gmail_user}")
        
        server.quit()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"❌ Error type: {type(e)}")
        
        # Provide specific troubleshooting tips
        if "535" in str(e):
            print("\n🔍 Troubleshooting tips:")
            print("1. Controleer of 2-Step Verification is ingeschakeld")
            print("2. Controleer of het app password correct is")
            print("3. Controleer Google Workspace admin instellingen")
        elif "530" in str(e):
            print("\n🔍 Troubleshooting tips:")
            print("1. Controleer of SMTP toegang is toegestaan")
            print("2. Controleer Google Workspace admin instellingen")

if __name__ == "__main__":
    test_correct_smtp()
