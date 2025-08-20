#!/usr/bin/env python3
"""
Dashboard Integration for TutorBot

This module handles sending lesson data to the dashboard API
"""

import os
import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional

class DashboardIntegration:
    """Integration with the privelessen-dashboard"""
    
    def __init__(self):
        self.dashboard_url = os.getenv("DASHBOARD_API_URL", "http://host.docker.internal:4141")
        self.api_key = os.getenv("DASHBOARD_API_KEY", "")
        
    def send_lesson_to_dashboard(self, lesson_data: Dict[str, Any]) -> bool:
        """
        Send lesson data to dashboard API
        
        Args:
            lesson_data: Dictionary containing lesson information
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            url = f"{self.dashboard_url}/api/tutorbot/lesson"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            response = requests.post(
                url,
                json=lesson_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Lesson sent to dashboard: {result.get('lesson', {}).get('id', 'unknown')}")
                return True
            else:
                print(f"❌ Failed to send lesson to dashboard: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending lesson to dashboard: {e}")
            return False
    
    def create_lesson_data(self, 
                          student_name: str,
                          student_email: str,
                          start_time: str,
                          end_time: str,
                          lesson_type: str,
                          chatwoot_contact_id: Optional[str] = None,
                          chatwoot_conversation_id: Optional[str] = None,
                          notes: str = "",
                          location: str = "Online",
                          program: Optional[str] = None,
                          topic_primary: Optional[str] = None,
                          topic_secondary: Optional[str] = None,
                          toolset: Optional[str] = None,
                          lesson_mode: str = "ONLINE",
                          is_adult: bool = False,
                          relationship_to_learner: Optional[str] = None) -> Dict[str, Any]:
        """
        Create lesson data structure for dashboard
        
        Args:
            student_name: Name of the student
            student_email: Email of the student
            start_time: Start time in ISO format
            end_time: End time in ISO format
            lesson_type: 'trial' or 'regular'
            chatwoot_contact_id: Chatwoot contact ID
            chatwoot_conversation_id: Chatwoot conversation ID
            notes: Additional notes
            location: Lesson location
            program: Educational program
            topic_primary: Primary topic
            topic_secondary: Secondary topic
            toolset: Tools used
            lesson_mode: 'ONLINE', 'IN_PERSON', or 'HYBRID'
            is_adult: Whether student is adult
            relationship_to_learner: Relationship to learner
            
        Returns:
            Dict containing lesson data
        """
        return {
            "student_name": student_name,
            "student_email": student_email,
            "start_time": start_time,
            "end_time": end_time,
            "lesson_type": lesson_type,
            "chatwoot_contact_id": chatwoot_contact_id,
            "chatwoot_conversation_id": chatwoot_conversation_id,
            "notes": notes,
            "location": location,
            "program": program,
            "topic_primary": topic_primary,
            "topic_secondary": topic_secondary,
            "toolset": toolset,
            "lesson_mode": lesson_mode,
            "is_adult": is_adult,
            "relationship_to_learner": relationship_to_learner
        }

# Global instance
dashboard = DashboardIntegration()

def send_lesson_to_dashboard(lesson_data: Dict[str, Any]) -> bool:
    """Convenience function to send lesson to dashboard"""
    return dashboard.send_lesson_to_dashboard(lesson_data)

def create_lesson_data(**kwargs) -> Dict[str, Any]:
    """Convenience function to create lesson data"""
    return dashboard.create_lesson_data(**kwargs)
