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
    """Test sending lesson data to dashboard"""
    
    # Set environment variables for testing
    os.environ.setdefault("DASHBOARD_API_URL", "http://localhost:4141")
    os.environ.setdefault("DASHBOARD_API_KEY", "test-key-123")
    
    print("🧪 Testing Dashboard Integration")
    print("=" * 50)
    
    # Create test lesson data
    start_time = datetime.now() + timedelta(days=1, hours=14)  # Tomorrow 2 PM
    end_time = start_time + timedelta(hours=1)  # 1 hour lesson
    
    lesson_data = create_lesson_data(
        student_name="Test Student",
        student_email="test@example.com",
        start_time=start_time.isoformat(),
        end_time=end_time.isoformat(),
        lesson_type="trial",
        chatwoot_contact_id="12345",
        chatwoot_conversation_id="67890",
        notes="Test proefles voor wiskunde",
        location="Online",
        program="trial",
        topic_primary="math",
        topic_secondary="wiskunde B",
        toolset="none",
        lesson_mode="ONLINE",
        is_adult=False,
        relationship_to_learner="self"
    )
    
    print(f"📋 Created lesson data:")
    print(f"   Student: {lesson_data['student_name']}")
    print(f"   Start: {lesson_data['start_time']}")
    print(f"   End: {lesson_data['end_time']}")
    print(f"   Type: {lesson_data['lesson_type']}")
    print(f"   Topic: {lesson_data['topic_secondary']}")
    
    # Send to dashboard
    print("\n🚀 Sending to dashboard...")
    success = send_lesson_to_dashboard(lesson_data)
    
    if success:
        print("✅ Successfully sent lesson to dashboard!")
        print("\n📊 Check the dashboard at: http://localhost:4141/dashboard/lessons")
    else:
        print("❌ Failed to send lesson to dashboard")
        print("💡 Make sure the dashboard is running on http://localhost:4141")
    
    return success

def test_multiple_lessons():
    """Test sending multiple lessons"""
    
    print("\n🧪 Testing Multiple Lessons")
    print("=" * 50)
    
    lessons = [
        {
            "student_name": "Anna de Vries",
            "student_email": "anna@example.com",
            "lesson_type": "trial",
            "topic_secondary": "Engels",
            "notes": "Proefles Engels voor IB diploma"
        },
        {
            "student_name": "Bram Jansen",
            "student_email": "bram@example.com", 
            "lesson_type": "regular",
            "topic_secondary": "Wiskunde B",
            "notes": "Reguliere les wiskunde B, hoofdstuk 5"
        },
        {
            "student_name": "Lisa Bakker",
            "student_email": "lisa@example.com",
            "lesson_type": "trial",
            "topic_secondary": "Statistiek",
            "notes": "Proefles statistiek voor universiteit"
        }
    ]
    
    for i, lesson_info in enumerate(lessons):
        start_time = datetime.now() + timedelta(days=i+1, hours=15)
        end_time = start_time + timedelta(hours=1)
        
        lesson_data = create_lesson_data(
            student_name=lesson_info["student_name"],
            student_email=lesson_info["student_email"],
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            lesson_type=lesson_info["lesson_type"],
            chatwoot_contact_id=f"contact_{i+1}",
            chatwoot_conversation_id=f"conv_{i+1}",
            notes=lesson_info["notes"],
            location="Online",
            program=lesson_info["lesson_type"],
            topic_primary="math" if "wiskunde" in lesson_info["topic_secondary"].lower() else "english",
            topic_secondary=lesson_info["topic_secondary"],
            toolset="none",
            lesson_mode="ONLINE",
            is_adult=False,
            relationship_to_learner="self"
        )
        
        print(f"\n📝 Sending lesson {i+1}: {lesson_info['student_name']}")
        success = send_lesson_to_dashboard(lesson_data)
        
        if success:
            print(f"✅ Lesson {i+1} sent successfully")
        else:
            print(f"❌ Failed to send lesson {i+1}")

if __name__ == "__main__":
    print("🎯 Dashboard Integration Test")
    print("=" * 50)
    
    # Test single lesson
    success = test_dashboard_integration()
    
    if success:
        # Test multiple lessons
        test_multiple_lessons()
        
        print("\n🎉 All tests completed!")
        print("📊 Check your dashboard at: http://localhost:4141/dashboard/lessons")
    else:
        print("\n❌ Basic test failed, skipping multiple lessons test")
        print("💡 Make sure:")
        print("   1. Dashboard is running on http://localhost:4141")
        print("   2. Database is properly configured")
        print("   3. API endpoints are accessible")
