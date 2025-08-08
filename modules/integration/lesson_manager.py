"""
Lesson Manager

Integrates calendar and notes functionality for complete
lesson management workflow.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from ..calendar import CalendarManager, EventCreator, StatusManager
from ..notes import NotesManager, DriveBackup, NoteOrganizer

class LessonManager:
    """Manages complete lesson workflow including calendar and notes"""
    
    def __init__(self):
        # Initialize all components
        self.calendar_manager = CalendarManager()
        self.event_creator = EventCreator(self.calendar_manager)
        self.status_manager = StatusManager(self.calendar_manager)
        
        self.notes_manager = NotesManager()
        self.drive_backup = DriveBackup(self.notes_manager)
        self.note_organizer = NoteOrganizer()
    
    def schedule_trial_lesson(self,
                             student_name: str,
                             start_time: datetime,
                             duration_minutes: int = 30,
                             location: str = "Zoom",
                             description: str = "",
                             auto_create_notes: bool = True) -> Dict[str, Any]:
        """
        Schedule a complete trial lesson with calendar and notes
        
        Args:
            student_name: Name of the student
            start_time: Start time of the lesson
            duration_minutes: Duration in minutes
            location: Location of the lesson
            description: Additional description
            auto_create_notes: Whether to automatically create note structure
            
        Returns:
            Dictionary with results
        """
        result = {
            'success': False,
            'calendar_event_id': None,
            'notes_link': None,
            'note_template_id': None,
            'errors': []
        }
        
        try:
            # 1. Create calendar event
            event_id = self.event_creator.create_trial_lesson(
                student_name=student_name,
                start_time=start_time,
                duration_minutes=duration_minutes,
                location=location,
                description=description
            )
            
            if event_id:
                result['calendar_event_id'] = event_id
                print(f"✅ Created trial lesson calendar event: {event_id}")
            else:
                result['errors'].append("Failed to create calendar event")
            
            # 2. Setup notes structure
            if auto_create_notes:
                notes_link = self.notes_manager.get_notes_link(student_name)
                result['notes_link'] = notes_link
                
                # Create note template
                note_template = self.note_organizer.create_trial_lesson_template(
                    student_name, start_time, "Trial Lesson"
                )
                
                note_id = self.notes_manager.create_lesson_note(
                    student_name=student_name,
                    lesson_date=start_time,
                    lesson_topic="Trial Lesson",
                    note_content=note_template
                )
                
                if note_id:
                    result['note_template_id'] = note_id
                    print(f"✅ Created trial lesson note template: {note_id}")
                else:
                    result['errors'].append("Failed to create note template")
            
            result['success'] = len(result['errors']) == 0
            
        except Exception as e:
            result['errors'].append(f"Trial lesson scheduling failed: {str(e)}")
        
        return result
    
    def schedule_intake_session(self,
                               student_name: str,
                               start_time: datetime,
                               duration_minutes: int = 45,
                               location: str = "",
                               description: str = "",
                               auto_create_notes: bool = True) -> Dict[str, Any]:
        """
        Schedule an intake session with calendar and notes
        
        Args:
            student_name: Name of the student
            start_time: Start time of the session
            duration_minutes: Duration in minutes
            location: Location of the session
            description: Additional description
            auto_create_notes: Whether to automatically create note structure
            
        Returns:
            Dictionary with results
        """
        result = {
            'success': False,
            'calendar_event_id': None,
            'notes_link': None,
            'note_template_id': None,
            'errors': []
        }
        
        try:
            # 1. Create calendar event
            event_id = self.event_creator.create_intake_session(
                student_name=student_name,
                start_time=start_time,
                duration_minutes=duration_minutes,
                location=location,
                description=description
            )
            
            if event_id:
                result['calendar_event_id'] = event_id
                print(f"✅ Created intake session calendar event: {event_id}")
            else:
                result['errors'].append("Failed to create calendar event")
            
            # 2. Setup notes structure
            if auto_create_notes:
                notes_link = self.notes_manager.get_notes_link(student_name)
                result['notes_link'] = notes_link
                
                # Create intake template
                note_template = self.note_organizer.create_intake_template(
                    student_name, start_time
                )
                
                note_id = self.notes_manager.create_lesson_note(
                    student_name=student_name,
                    lesson_date=start_time,
                    lesson_topic="Intake Session",
                    note_content=note_template
                )
                
                if note_id:
                    result['note_template_id'] = note_id
                    print(f"✅ Created intake session note template: {note_id}")
                else:
                    result['errors'].append("Failed to create note template")
            
            result['success'] = len(result['errors']) == 0
            
        except Exception as e:
            result['errors'].append(f"Intake session scheduling failed: {str(e)}")
        
        return result
    
    def schedule_regular_lesson(self,
                               student_name: str,
                               lesson_topic: str,
                               start_time: datetime,
                               duration_minutes: int = 60,
                               location: str = "",
                               description: str = "",
                               is_confirmed: bool = False,
                               auto_create_notes: bool = True) -> Dict[str, Any]:
        """
        Schedule a regular lesson with calendar and notes
        
        Args:
            student_name: Name of the student
            lesson_topic: Topic of the lesson
            start_time: Start time of the lesson
            duration_minutes: Duration in minutes
            location: Location of the lesson
            description: Additional description
            is_confirmed: Whether the lesson is confirmed/paid
            auto_create_notes: Whether to automatically create note structure
            
        Returns:
            Dictionary with results
        """
        result = {
            'success': False,
            'calendar_event_id': None,
            'notes_link': None,
            'note_template_id': None,
            'errors': []
        }
        
        try:
            # 1. Create calendar event
            event_id = self.event_creator.create_regular_lesson(
                student_name=student_name,
                lesson_type=lesson_topic,
                start_time=start_time,
                duration_minutes=duration_minutes,
                location=location,
                description=description,
                is_confirmed=is_confirmed
            )
            
            if event_id:
                result['calendar_event_id'] = event_id
                print(f"✅ Created regular lesson calendar event: {event_id}")
            else:
                result['errors'].append("Failed to create calendar event")
            
            # 2. Setup notes structure
            if auto_create_notes:
                notes_link = self.notes_manager.get_notes_link(student_name)
                result['notes_link'] = notes_link
                
                # Create regular lesson template
                note_template = self.note_organizer.create_note_template(
                    student_name, start_time, lesson_topic, "regular"
                )
                
                note_id = self.notes_manager.create_lesson_note(
                    student_name=student_name,
                    lesson_date=start_time,
                    lesson_topic=lesson_topic,
                    note_content=note_template
                )
                
                if note_id:
                    result['note_template_id'] = note_id
                    print(f"✅ Created regular lesson note template: {note_id}")
                else:
                    result['errors'].append("Failed to create note template")
            
            result['success'] = len(result['errors']) == 0
            
        except Exception as e:
            result['errors'].append(f"Regular lesson scheduling failed: {str(e)}")
        
        return result
    
    def confirm_lesson(self, event_id: str) -> bool:
        """
        Confirm a lesson (change status to definitief)
        
        Args:
            event_id: Calendar event ID
            
        Returns:
            True if successful
        """
        return self.status_manager.confirm_lesson(event_id)
    
    def get_lesson_summary(self, student_name: str) -> Dict[str, Any]:
        """
        Get comprehensive lesson summary for a student
        
        Args:
            student_name: Name of the student
            
        Returns:
            Dictionary with lesson summary
        """
        summary = {
            'student_name': student_name,
            'notes_link': self.notes_manager.get_notes_link(student_name),
            'backup_status': self.drive_backup.get_backup_status(student_name),
            'recent_notes': [],
            'upcoming_lessons': [],
            'total_lessons': 0
        }
        
        try:
            # Get recent notes
            notes = self.notes_manager.list_student_notes(student_name)
            summary['recent_notes'] = notes[:5] if notes else []
            summary['total_lessons'] = len(notes)
            
            # Get upcoming lessons (this would require calendar query)
            # For now, we'll leave this empty
            summary['upcoming_lessons'] = []
            
        except Exception as e:
            print(f"❌ Failed to get lesson summary: {e}")
        
        return summary
    
    def backup_lesson_files(self,
                           student_name: str,
                           lesson_date: datetime,
                           lesson_topic: str,
                           file_paths: List[str]) -> List[str]:
        """
        Backup lesson files to Google Drive
        
        Args:
            student_name: Name of the student
            lesson_date: Date of the lesson
            lesson_topic: Topic of the lesson
            file_paths: List of file paths to backup
            
        Returns:
            List of successful file IDs
        """
        return self.drive_backup.backup_lesson_files(
            student_name, lesson_date, lesson_topic, file_paths
        )
    
    def get_available_slots(self, date: datetime, duration_minutes: int = 60) -> List[Dict[str, Any]]:
        """
        Get available time slots for a given date
        
        Args:
            date: Date to check
            duration_minutes: Duration needed
            
        Returns:
            List of available slots
        """
        return self.calendar_manager.get_available_slots(date, duration_minutes)
