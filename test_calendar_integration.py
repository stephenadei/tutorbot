#!/usr/bin/env python3
"""
Test Google Calendar Integration

This script tests if the Google Calendar integration is properly configured
and can access the calendar for the lessons@stephensprivelessen.nl account.
"""

import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_calendar_config():
    """Test calendar configuration"""
    print("🔍 Testing Google Calendar Configuration...")
    
    # Check environment variables
    gcal_json = os.getenv("GCAL_SERVICE_ACCOUNT_JSON")
    gcal_calendar_id = os.getenv("GCAL_CALENDAR_ID", "primary")
    
    print(f"📁 Service Account JSON path: {gcal_json}")
    print(f"📅 Calendar ID: {gcal_calendar_id}")
    
    if not gcal_json:
        print("❌ GCAL_SERVICE_ACCOUNT_JSON not set")
        return False
    
    # Check if service account file exists
    if not os.path.exists(gcal_json):
        print(f"❌ Service account file not found: {gcal_json}")
        return False
    
    print("✅ Service account file exists")
    return True

def test_calendar_access():
    """Test calendar access"""
    print("\n🔍 Testing Calendar Access...")
    
    try:
        from modules.calendar.calendar_manager import CalendarManager
        
        # Initialize calendar manager
        calendar_manager = CalendarManager()
        
        if not calendar_manager.service:
            print("❌ Failed to initialize Google Calendar service")
            return False
        
        print("✅ Google Calendar service initialized")
        
        # Test calendar access by listing events
        now = datetime.now(ZoneInfo("Europe/Amsterdam"))
        time_min = now.isoformat()
        time_max = (now + timedelta(days=7)).isoformat()
        
        events_result = calendar_manager.service.events().list(
            calendarId=calendar_manager.calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=5,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"✅ Successfully accessed calendar - found {len(events)} events in next 7 days")
        
        # Test creating a test event
        test_start = now + timedelta(hours=1)
        event_id = calendar_manager.create_lesson_event(
            student_name="TEST STUDENT",
            lesson_type="test",
            status="test",
            start_time=test_start,
            duration_minutes=30,
            location="Test Location",
            description="Test event for calendar integration"
        )
        
        if event_id:
            print(f"✅ Successfully created test event: {event_id}")
            
            # Clean up - delete the test event
            calendar_manager.service.events().delete(
                calendarId=calendar_manager.calendar_id,
                eventId=event_id
            ).execute()
            print("✅ Test event cleaned up")
        else:
            print("❌ Failed to create test event")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Calendar access test failed: {e}")
        return False

def test_email_config():
    """Test email configuration"""
    print("\n🔍 Testing Email Configuration...")
    
    # Check if we have email-related environment variables
    email_vars = [
        "GMAIL_USER",
        "GMAIL_PASSWORD", 
        "GMAIL_APP_PASSWORD",
        "SMTP_SERVER",
        "SMTP_PORT"
    ]
    
    for var in email_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * len(value)}")  # Hide actual values
        else:
            print(f"❌ {var}: Not set")
    
    return True

def main():
    """Main test function"""
    print("🚀 Testing Google Workspace Integration for lessons@stephensprivelessen.nl")
    print("=" * 70)
    
    # Test calendar configuration
    config_ok = test_calendar_config()
    
    # Test calendar access
    calendar_ok = False
    if config_ok:
        calendar_ok = test_calendar_access()
    
    # Test email configuration
    email_ok = test_email_config()
    
    print("\n" + "=" * 70)
    print("📊 Test Results:")
    print(f"📁 Configuration: {'✅ OK' if config_ok else '❌ FAILED'}")
    print(f"📅 Calendar Access: {'✅ OK' if calendar_ok else '❌ FAILED'}")
    print(f"📧 Email Config: {'✅ OK' if email_ok else '❌ FAILED'}")
    
    if config_ok and calendar_ok:
        print("\n🎉 Google Calendar integration is working!")
        print("✅ You can create calendar events")
        print("✅ You can read calendar events")
        print("✅ Calendar is properly configured")
    else:
        print("\n⚠️  Google Calendar integration needs attention")
        print("❌ Check the service account configuration")
        print("❌ Verify the calendar permissions")
    
    if not email_ok:
        print("\n⚠️  Email configuration needs attention")
        print("❌ Set up Gmail SMTP credentials for email sending")

if __name__ == "__main__":
    main()
