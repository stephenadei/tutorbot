#!/usr/bin/env python3
"""
Simple SMTP Test
"""

import smtplib
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_smtp():
    """Test SMTP connection"""
    print("🔍 Testing SMTP Connection...")
    
    # Get credentials
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    print(f"📧 User: {gmail_user}")
    print(f"🔑 Password: {gmail_password[:4]}...{gmail_password[-4:] if gmail_password else 'None'}")
    
    try:
        # Create SMTP connection
        print("🔗 Connecting to Gmail SMTP...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        
        print("🔐 Attempting login...")
        server.login(gmail_user, gmail_password)
        
        print("✅ Login successful!")
        
        # Send test email
        print("📤 Sending test email...")
        server.sendmail(gmail_user, gmail_user, 
                       "Subject: Test Email\n\nThis is a test email from TutorBot.")
        
        print("✅ Test email sent successfully!")
        server.quit()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"❌ Error type: {type(e)}")

if __name__ == "__main__":
    test_smtp()
