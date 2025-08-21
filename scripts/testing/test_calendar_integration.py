#!/usr/bin/env python3
"""
Test Calendar Integration

This script tests the Google Calendar integration functionality
"""

import os
import sys
from datetime import datetime, timedelta
from calendar_integration import get_available_slots, calendar_integration

def test_calendar_integration():
    """Test the calendar integration"""
    print("🧪 Testing Calendar Integration")
    print("=" * 50)
    
    # Test date range
    now = datetime.now()
    start_date = now + timedelta(days=1)
    end_date = now + timedelta(days=7)
    
    print(f"📅 Testing availability from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Test scenarios
    scenarios = [
        {
            "name": "Trial lesson with evening preference",
            "lesson_type": "trial",
            "preferred_times": ["17:00", "18:00"],
            "description": "Should find weekday slots 17:00-19:00"
        },
        {
            "name": "Regular lesson with afternoon preference",
            "lesson_type": "regular",
            "preferred_times": ["14:00", "15:00", "16:00"],
            "description": "Should find weekday slots 14:00-20:00"
        },
        {
            "name": "Urgent lesson any time",
            "lesson_type": "urgent",
            "preferred_times": None,
            "description": "Should find slots any day 14:00-20:00"
        },
        {
            "name": "No preferences",
            "lesson_type": "trial",
            "preferred_times": None,
            "description": "Should find default trial slots"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 Scenario {i}: {scenario['name']}")
        print(f"   Description: {scenario['description']}")
        print(f"   Lesson type: {scenario['lesson_type']}")
        print(f"   Preferred times: {scenario['preferred_times']}")
        
        try:
            slots = get_available_slots(
                start_date=start_date,
                end_date=end_date,
                preferred_times=scenario['preferred_times'],
                lesson_type=scenario['lesson_type']
            )
            
            print(f"   ✅ Found {len(slots)} available slots")
            
            if slots:
                print(f"   📅 Sample slots:")
                for slot in slots[:3]:  # Show first 3 slots
                    print(f"      • {slot['label']}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test calendar service status
    print(f"\n🔧 Calendar Service Status:")
    if calendar_integration.service:
        print(f"   ✅ Google Calendar service is available")
        print(f"   📅 Calendar ID: {calendar_integration.calendar_id}")
    else:
        print(f"   ⚠️ Using mock calendar service")
        print(f"   💡 To enable real calendar:")
        print(f"      1. Create Google Cloud Project")
        print(f"      2. Enable Calendar API")
        print(f"      3. Create service account")
        print(f"      4. Download service-account-key.json")
        print(f"      5. Share calendar with service account email")
    
    print(f"\n🎯 Calendar Integration Test Complete!")

if __name__ == "__main__":
    test_calendar_integration()
