"""
Google Calendar Manager

Handles all calendar operations including lesson scheduling,
color coding, and status management.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from google.oauth2 import service_account
from googleapiclient.discovery import build
from zoneinfo import ZoneInfo

class CalendarManager:
    """Main calendar management class"""
    
    def __init__(self):
        self.service_account_json = os.getenv("GCAL_SERVICE_ACCOUNT_JSON")
        self.calendar_id = os.getenv("GCAL_CALENDAR_ID", "primary")
        self.timezone = ZoneInfo("Europe/Amsterdam")
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Calendar service"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_json,
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            self.service = build('calendar', 'v3', credentials=credentials)
            print("✅ Google Calendar service initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Google Calendar service: {e}")
            self.service = None
    
    def create_lesson_event(self, 
                           student_name: str,
                           lesson_type: str,
                           status: str,
                           start_time: datetime,
                           duration_minutes: int = 60,
                           location: str = "",
                           description: str = "",
                           notes_link: str = "") -> Optional[str]:
        """
        Create a lesson event with proper formatting and color coding
        
        Args:
            student_name: Name of the student
            lesson_type: Type of lesson (wiskunde, intake, etc.)
            status: Status (definitief, voorstel, proefles, etc.)
            start_time: Start time of the lesson
            duration_minutes: Duration in minutes
            location: Location (Zoom, physical location, etc.)
            description: Additional description
            notes_link: Link to Notability notes
            
        Returns:
            Event ID if successful, None otherwise
        """
        if not self.service:
            print("❌ Calendar service not available")
            return None
        
        # Format title according to specification
        title = self._format_event_title(student_name, lesson_type, status, location)
        
        # Get color based on status
        color_id = self._get_color_for_status(status)
        
        # Format description
        full_description = self._format_description(description, notes_link)
        
        # Calculate end time
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        event = {
            'summary': title,
            'description': full_description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': str(self.timezone),
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': str(self.timezone),
            },
            'colorId': color_id,
            'location': location if location else None,
        }
        
        try:
            event_result = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            event_id = event_result.get('id')
            print(f"✅ Created calendar event: {title} (ID: {event_id})")
            return event_id
            
        except Exception as e:
            print(f"❌ Failed to create calendar event: {e}")
            return None
    
    def update_event_status(self, event_id: str, new_status: str) -> bool:
        """
        Update the status of an existing event
        
        Args:
            event_id: Google Calendar event ID
            new_status: New status (definitief, voorstel, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            return False
        
        try:
            # Get current event
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            # Update title with new status
            current_title = event.get('summary', '')
            new_title = self._update_title_status(current_title, new_status)
            
            # Update color
            new_color = self._get_color_for_status(new_status)
            
            # Update event
            event['summary'] = new_title
            event['colorId'] = new_color
            
            self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            print(f"✅ Updated event status: {new_status}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update event status: {e}")
            return False
    
    def _format_event_title(self, student_name: str, lesson_type: str, 
                           status: str, location: str) -> str:
        """Format event title according to specification"""
        title_parts = [student_name, lesson_type]
        
        if status:
            title_parts.append(status)
        
        if location:
            title_parts.append(location)
        
        return " – ".join(title_parts)
    
    def _update_title_status(self, current_title: str, new_status: str) -> str:
        """Update status in existing title"""
        parts = current_title.split(" – ")
        if len(parts) >= 3:
            # Replace status (third part)
            parts[2] = new_status
        else:
            # Add status if not present
            parts.append(new_status)
        
        return " – ".join(parts)
    
    def _get_color_for_status(self, status: str) -> str:
        """Get Google Calendar color ID based on status"""
        color_mapping = {
            "definitief": "5",      # Yellow
            "voorstel": "11",       # Red
            "proefles": "1",        # Blue
            "intake": "1",          # Blue
            "schoolles": "3",       # Green
            "vervanging": "8",      # Gray
            "follow-up": "6",       # Purple
            "herinnering": "6",     # Purple
        }
        
        return color_mapping.get(status.lower(), "5")  # Default to yellow
    
    def _format_description(self, description: str, notes_link: str) -> str:
        """Format event description with notes link"""
        desc_parts = []
        
        if description:
            desc_parts.append(description)
        
        if notes_link:
            desc_parts.append(f"\nNotities: {notes_link}")
        
        return "\n".join(desc_parts) if desc_parts else ""
    
    def get_available_slots(self, date: datetime, duration_minutes: int = 60) -> List[Dict[str, Any]]:
        """
        Get available time slots for a given date
        
        Args:
            date: Date to check
            duration_minutes: Duration of slots needed
            
        Returns:
            List of available time slots
        """
        if not self.service:
            return []
        
        # Define business hours (9:00-18:00)
        start_of_day = date.replace(hour=9, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=18, minute=0, second=0, microsecond=0)
        
        # Get existing events for the day
        events_result = self.service.events().list(
            calendarId=self.calendar_id,
            timeMin=start_of_day.isoformat(),
            timeMax=end_of_day.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Generate available slots
        available_slots = []
        current_time = start_of_day
        
        while current_time + timedelta(minutes=duration_minutes) <= end_of_day:
            slot_end = current_time + timedelta(minutes=duration_minutes)
            
            # Check if slot conflicts with existing events
            conflict = False
            for event in events:
                event_start = datetime.fromisoformat(
                    event['start']['dateTime'].replace('Z', '+00:00')
                ).replace(tzinfo=self.timezone)
                event_end = datetime.fromisoformat(
                    event['end']['dateTime'].replace('Z', '+00:00')
                ).replace(tzinfo=self.timezone)
                
                if (current_time < event_end and slot_end > event_start):
                    conflict = True
                    break
            
            if not conflict:
                available_slots.append({
                    'start': current_time,
                    'end': slot_end,
                    'duration': duration_minutes
                })
            
            # Move to next slot (30-minute intervals)
            current_time += timedelta(minutes=30)
        
        return available_slots
