#!/usr/bin/env python3
"""
Test Dashboard Integration

This script tests the integration between TutorBot and the dashboard
"""

import os
import sys
from datetime import datetime, timedelta
from dashboard_integration import create_lesson_data, send_lesson_to_dashboard

def test_dashboard_integration():
    """Test the dashboard integration"""
    print("🧪 Testing Dashboard Integration")
    print("=" * 50)
    
    # Test data
    start_time = (datetime.now() + timedelta(days=1)).isoformat()
    end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
    
    lesson_data = create_lesson_data(
        student_name="Test Student",
        student_email="test@example.com",
        start_time=start_time,
        end_time=end_time,
        lesson_type="trial",
        chatwoot_contact_id="123",
        chatwoot_conversation_id="456",
        notes="Test lesson from TutorBot",
        location="Online",
        program="MBO_REKENEN_2F",
        topic_primary="Wiskunde",
        topic_secondary="Algebra",
        toolset="Geogebra",
        lesson_mode="ONLINE",
        is_adult=False,
        relationship_to_learner="student"
    )
    
    print(f"📋 Created lesson data:")
    print(f"   Student: {lesson_data['studentName']}")
    print(f"   Email: {lesson_data['studentEmail']}")
    print(f"   Start: {lesson_data['startTime']}")
    print(f"   End: {lesson_data['endTime']}")
    print(f"   Type: {lesson_data['lessonType']}")
    print(f"   Program: {lesson_data['program']}")
    print(f"   Topic: {lesson_data['topicPrimary']}")
    
    # Test sending to dashboard
    print(f"\n📤 Sending to dashboard...")
    success = send_lesson_to_dashboard(lesson_data)
    
    if success:
        print("✅ Successfully sent lesson to dashboard!")
    else:
        print("❌ Failed to send lesson to dashboard")
        print("   Make sure the dashboard is running on http://localhost:4141")
    
    return success

if __name__ == "__main__":
    test_dashboard_integration()
