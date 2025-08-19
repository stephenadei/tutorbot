#!/usr/bin/env python3
"""
Test Email Delivery

This script tests email delivery with different configurations
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def test_basic_smtp():
    """Test basic SMTP connection and sending"""
    print("🔍 Testing Basic SMTP...")
    
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    print(f"📧 From: {gmail_user}")
    print(f"🔑 Password: {'SET' if gmail_password else 'NOT SET'}")
    
    try:
        # Create connection
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls(context=ssl.create_default_context())
        server.login(gmail_user, gmail_password)
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = "stephen@stephenadei.nl"
        msg['Subject'] = f"Basic SMTP Test - {datetime.now().strftime('%H:%M:%S')}"
        
        body = f"""
Hi,

This is a basic SMTP test email.

Time: {datetime.now()}
From: {gmail_user}
To: stephen@stephenadei.nl

Best regards,
TutorBot
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        text = msg.as_string()
        server.sendmail(gmail_user, "stephen@stephenadei.nl", text)
        server.quit()
        
        print("✅ Basic SMTP test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Basic SMTP test failed: {e}")
        return False

def test_with_display_name():
    """Test with display name in From field"""
    print("\n🔍 Testing with Display Name...")
    
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls(context=ssl.create_default_context())
        server.login(gmail_user, gmail_password)
        
        msg = MIMEMultipart()
        msg['From'] = f"TutorBot Test <{gmail_user}>"
        msg['To'] = "stephen@stephenadei.nl"
        msg['Subject'] = f"Display Name Test - {datetime.now().strftime('%H:%M:%S')}"
        
        body = f"""
Hi,

This is a test with display name in From field.

Time: {datetime.now()}
From: TutorBot Test <{gmail_user}>
To: stephen@stephenadei.nl

Best regards,
TutorBot
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        text = msg.as_string()
        server.sendmail(gmail_user, "stephen@stephenadei.nl", text)
        server.quit()
        
        print("✅ Display name test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Display name test failed: {e}")
        return False

def test_to_gmail():
    """Test sending to Gmail"""
    print("\n🔍 Testing to Gmail...")
    
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls(context=ssl.create_default_context())
        server.login(gmail_user, gmail_password)
        
        msg = MIMEMultipart()
        msg['From'] = f"TutorBot Test <{gmail_user}>"
        msg['To'] = "stephenadei@gmail.com"
        msg['Subject'] = f"Gmail Test - {datetime.now().strftime('%H:%M:%S')}"
        
        body = f"""
Hi Stephen,

This is a test email to Gmail.

Time: {datetime.now()}
From: TutorBot Test <{gmail_user}>
To: stephenadei@gmail.com

Please check if you receive this email.

Best regards,
TutorBot
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        text = msg.as_string()
        server.sendmail(gmail_user, "stephenadei@gmail.com", text)
        server.quit()
        
        print("✅ Gmail test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Gmail test failed: {e}")
        return False

def test_simple_subject():
    """Test with simple subject to avoid spam filters"""
    print("\n🔍 Testing Simple Subject...")
    
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls(context=ssl.create_default_context())
        server.login(gmail_user, gmail_password)
        
        msg = MIMEMultipart()
        msg['From'] = f"Stephen <{gmail_user}>"
        msg['To'] = "stephenadei@gmail.com"
        msg['Subject'] = "Test"
        
        body = f"""
Hi,

Simple test email.

Time: {datetime.now()}

Best regards,
Stephen
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        text = msg.as_string()
        server.sendmail(gmail_user, "stephenadei@gmail.com", text)
        server.quit()
        
        print("✅ Simple subject test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Simple subject test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Email Delivery Test")
    print("=" * 50)
    
    tests = [
        test_basic_smtp,
        test_with_display_name,
        test_to_gmail,
        test_simple_subject
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Basic SMTP: {'✅ PASS' if results[0] else '❌ FAIL'}")
    print(f"Display Name: {'✅ PASS' if results[1] else '❌ FAIL'}")
    print(f"Gmail Delivery: {'✅ PASS' if results[2] else '❌ FAIL'}")
    print(f"Simple Subject: {'✅ PASS' if results[3] else '❌ FAIL'}")
    
    if all(results):
        print("\n🎉 All tests passed!")
            print("📧 Check your email inboxes:")
    print("   - stephen@stephenadei.nl")
    print("   - lessen@stephensprivelessen.nl")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
