"""
Event Creator for specific lesson types

Handles creation of different types of calendar events
based on lesson type and status.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from .calendar_manager import CalendarManager

class EventCreator:
    """Creates specific types of calendar events"""
    
    def __init__(self, calendar_manager: CalendarManager):
        self.calendar = calendar_manager
    
    def create_trial_lesson(self, 
                           student_name: str,
                           start_time: datetime,
                           duration_minutes: int = 30,
                           location: str = "Zoom",
                           description: str = "",
                           notes_link: str = "") -> Optional[str]:
        """
        Create a trial lesson event
        
        Args:
            student_name: Name of the student
            start_time: Start time
            duration_minutes: Duration (default 30 min for trial)
            location: Location (default Zoom)
            description: Additional description
            notes_link: Link to notes
            
        Returns:
            Event ID if successful
        """
        return self.calendar.create_lesson_event(
            student_name=student_name,
            lesson_type="Proefles",
            status="proefles",
            start_time=start_time,
            duration_minutes=duration_minutes,
            location=location,
            description=description,
            notes_link=notes_link
        )
    
    def create_intake_session(self,
                             student_name: str,
                             start_time: datetime,
                             duration_minutes: int = 45,
                             location: str = "",
                             description: str = "",
                             notes_link: str = "") -> Optional[str]:
        """
        Create an intake session event
        
        Args:
            student_name: Name of the student
            start_time: Start time
            duration_minutes: Duration (default 45 min for intake)
            location: Location
            description: Additional description
            notes_link: Link to notes
            
        Returns:
            Event ID if successful
        """
        return self.calendar.create_lesson_event(
            student_name=student_name,
            lesson_type="Intake",
            status="intake",
            start_time=start_time,
            duration_minutes=duration_minutes,
            location=location,
            description=description,
            notes_link=notes_link
        )
    
    def create_regular_lesson(self,
                             student_name: str,
                             lesson_type: str,
                             start_time: datetime,
                             duration_minutes: int = 60,
                             location: str = "",
                             description: str = "",
                             notes_link: str = "",
                             is_confirmed: bool = False) -> Optional[str]:
        """
        Create a regular lesson event
        
        Args:
            student_name: Name of the student
            lesson_type: Type of lesson (wiskunde, engels, etc.)
            start_time: Start time
            duration_minutes: Duration (default 60 min)
            location: Location
            description: Additional description
            notes_link: Link to notes
            is_confirmed: Whether the lesson is confirmed/paid
            
        Returns:
            Event ID if successful
        """
        status = "definitief" if is_confirmed else "voorstel"
        
        return self.calendar.create_lesson_event(
            student_name=student_name,
            lesson_type=lesson_type,
            status=status,
            start_time=start_time,
            duration_minutes=duration_minutes,
            location=location,
            description=description,
            notes_link=notes_link
        )
    
    def create_school_lesson(self,
                            student_name: str,
                            school_name: str,
                            start_time: datetime,
                            duration_minutes: int = 60,
                            location: str = "",
                            description: str = "",
                            notes_link: str = "") -> Optional[str]:
        """
        Create a school-related lesson event
        
        Args:
            student_name: Name of the student
            school_name: Name of the school
            start_time: Start time
            duration_minutes: Duration
            location: Location
            description: Additional description
            notes_link: Link to notes
            
        Returns:
            Event ID if successful
        """
        return self.calendar.create_lesson_event(
            student_name=student_name,
            lesson_type=f"schoolles - {school_name}",
            status="schoolles",
            start_time=start_time,
            duration_minutes=duration_minutes,
            location=location,
            description=description,
            notes_link=notes_link
        )
    
    def create_substitution_lesson(self,
                                  original_student: str,
                                  substitute_teacher: str,
                                  start_time: datetime,
                                  duration_minutes: int = 60,
                                  location: str = "",
                                  description: str = "",
                                  notes_link: str = "") -> Optional[str]:
        """
        Create a substitution lesson event
        
        Args:
            original_student: Original student name
            substitute_teacher: Name of substitute teacher
            start_time: Start time
            duration_minutes: Duration
            location: Location
            description: Additional description
            notes_link: Link to notes
            
        Returns:
            Event ID if successful
        """
        desc = f"Vervanging door {substitute_teacher}\n{description}" if description else f"Vervanging door {substitute_teacher}"
        
        return self.calendar.create_lesson_event(
            student_name=original_student,
            lesson_type="Vervanging",
            status="vervanging",
            start_time=start_time,
            duration_minutes=duration_minutes,
            location=location,
            description=desc,
            notes_link=notes_link
        )
    
    def create_follow_up_reminder(self,
                                 student_name: str,
                                 reminder_type: str,
                                 due_date: datetime,
                                 description: str = "",
                                 notes_link: str = "") -> Optional[str]:
        """
        Create a follow-up or reminder event
        
        Args:
            student_name: Name of the student
            reminder_type: Type of reminder (follow-up, herinnering, etc.)
            due_date: Due date/time
            description: Description of what needs to be done
            notes_link: Link to related notes
            
        Returns:
            Event ID if successful
        """
        return self.calendar.create_lesson_event(
            student_name=student_name,
            lesson_type=reminder_type,
            status="follow-up",
            start_time=due_date,
            duration_minutes=15,  # Short reminder events
            location="",
            description=description,
            notes_link=notes_link
        )
