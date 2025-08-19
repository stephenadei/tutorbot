#!/usr/bin/env python3
"""
Calendar Integration for TutorBot

This module handles Google Calendar integration to check real availability
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pytz

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False
    print("⚠️ Google Calendar API not available - install google-auth and google-api-python-client")

class CalendarIntegration:
    """Google Calendar integration for checking real availability"""
    
    def __init__(self):
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "lessen@stephensprivelessen.nl")
        self.service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service-account-key.json")
        self.timezone = pytz.timezone('Europe/Amsterdam')
        
        if GOOGLE_CALENDAR_AVAILABLE:
            self.service = self._create_calendar_service()
        else:
            self.service = None
    
    def _create_calendar_service(self):
        """Create Google Calendar service"""
        try:
            if os.path.exists(self.service_account_file):
                credentials = service_account.Credentials.from_service_account_file(
                    self.service_account_file,
                    scopes=['https://www.googleapis.com/auth/calendar.readonly']
                )
                return build('calendar', 'v3', credentials=credentials)
            else:
                print(f"⚠️ Service account file not found: {self.service_account_file}")
                return None
        except Exception as e:
            print(f"❌ Error creating calendar service: {e}")
            return None
    
    def get_available_slots(self, start_date: datetime, end_date: datetime, 
                           preferred_times: List[str] = None, lesson_type: str = "trial") -> List[Dict[str, Any]]:
        """
        Get available slots from Google Calendar
        
        Args:
            start_date: Start date for availability check
            end_date: End date for availability check
            preferred_times: List of preferred times (e.g., ["17:00", "18:00"])
            lesson_type: Type of lesson ("trial", "regular", "urgent")
            
        Returns:
            List of available slots
        """
        if not self.service:
            print("⚠️ Calendar service not available - using mock slots")
            return self._get_mock_slots(start_date, end_date, preferred_times, lesson_type)
        
        try:
            # Get existing events
            events = self._get_calendar_events(start_date, end_date)
            
            # Generate potential slots
            potential_slots = self._generate_potential_slots(start_date, end_date, preferred_times, lesson_type)
            
            # Filter out occupied slots
            available_slots = self._filter_available_slots(potential_slots, events)
            
            print(f"📅 Found {len(available_slots)} available slots out of {len(potential_slots)} potential slots")
            return available_slots
            
        except Exception as e:
            print(f"❌ Error getting available slots: {e}")
            return self._get_mock_slots(start_date, end_date, preferred_times, lesson_type)
    
    def _get_calendar_events(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get events from Google Calendar"""
        try:
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            print(f"📅 Found {len(events)} existing events in calendar")
            return events
            
        except HttpError as error:
            print(f"❌ Error fetching calendar events: {error}")
            return []
    
    def _generate_potential_slots(self, start_date: datetime, end_date: datetime, 
                                 preferred_times: List[str] = None, lesson_type: str = "trial") -> List[Dict[str, Any]]:
        """Generate potential time slots"""
        slots = []
        current_date = start_date
        
        while current_date <= end_date:
            # Skip weekends for trial lessons
            if lesson_type == "trial" and current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue
            
            # Determine available hours based on lesson type
            if lesson_type == "trial":
                # Trial lessons: 17:00-19:00 on weekdays
                start_hour, end_hour = 17, 19
            elif lesson_type == "urgent":
                # Urgent lessons: 14:00-20:00 any day
                start_hour, end_hour = 14, 20
            else:
                # Regular lessons: 14:00-20:00 on weekdays
                start_hour, end_hour = 14, 20
                if current_date.weekday() >= 5:  # Weekend
                    start_hour, end_hour = 10, 18
            
            # Generate slots for this day
            for hour in range(start_hour, end_hour):
                for minute in [0, 30]:  # 30-minute intervals
                    slot_start = current_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    slot_end = slot_start + timedelta(hours=1)
                    
                    # Check if this time matches preferred times
                    if preferred_times:
                        slot_time_str = slot_start.strftime("%H:%M")
                        if not any(pref_time in slot_time_str for pref_time in preferred_times):
                            continue
                    
                    # Only add slots in the future
                    if slot_start > datetime.now(self.timezone):
                        slots.append({
                            "start": slot_start,
                            "end": slot_end,
                            "date": slot_start.date(),
                            "time": slot_start.strftime("%H:%M"),
                            "day_name": slot_start.strftime("%A")
                        })
            
            current_date += timedelta(days=1)
        
        return slots
    
    def _filter_available_slots(self, potential_slots: List[Dict[str, Any]], 
                               events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out slots that conflict with existing events"""
        available_slots = []
        
        for slot in potential_slots:
            slot_start = slot["start"]
            slot_end = slot["end"]
            
            # Check if slot conflicts with any existing event
            is_available = True
            for event in events:
                event_start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
                event_end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')))
                
                # Check for overlap
                if (slot_start < event_end and slot_end > event_start):
                    is_available = False
                    break
            
            if is_available:
                # Create readable label
                slot["label"] = f"{slot_start.strftime('%a %d %b %H:%M')}–{slot_end.strftime('%H:%M')}"
                slot["start_iso"] = slot_start.isoformat()
                slot["end_iso"] = slot_end.isoformat()
                available_slots.append(slot)
        
        return available_slots
    
    def _get_mock_slots(self, start_date: datetime, end_date: datetime, 
                       preferred_times: List[str] = None, lesson_type: str = "trial") -> List[Dict[str, Any]]:
        """Generate mock slots when calendar integration is not available"""
        slots = []
        current_date = start_date
        
        while current_date <= end_date and len(slots) < 8:
            # Skip weekends for trial lessons
            if lesson_type == "trial" and current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue
            
            # Generate mock slots
            for hour in [17, 18] if lesson_type == "trial" else [14, 15, 16, 17, 18]:
                slot_start = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                slot_end = slot_start + timedelta(hours=1)
                
                if slot_start > datetime.now(self.timezone):
                    slots.append({
                        "start": slot_start,
                        "end": slot_end,
                        "date": slot_start.date(),
                        "time": slot_start.strftime("%H:%M"),
                        "day_name": slot_start.strftime("%A"),
                        "label": f"{slot_start.strftime('%a %d %b %H:%M')}–{slot_end.strftime('%H:%M')}",
                        "start_iso": slot_start.isoformat(),
                        "end_iso": slot_end.isoformat(),
                        "mock": True
                    })
            
            current_date += timedelta(days=1)
        
        return slots

# Global instance
calendar_integration = CalendarIntegration()

def get_available_slots(start_date: datetime, end_date: datetime, 
                       preferred_times: List[str] = None, lesson_type: str = "trial") -> List[Dict[str, Any]]:
    """Convenience function to get available slots"""
    return calendar_integration.get_available_slots(start_date, end_date, preferred_times, lesson_type)
