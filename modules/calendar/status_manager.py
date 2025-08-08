"""
Status Manager for Calendar Events

Handles status transitions and workflow management
for calendar events.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from .calendar_manager import CalendarManager

class StatusManager:
    """Manages status transitions for calendar events"""
    
    def __init__(self, calendar_manager: CalendarManager):
        self.calendar = calendar_manager
    
    def confirm_lesson(self, event_id: str) -> bool:
        """
        Confirm a lesson (change from voorstel to definitief)
        
        Args:
            event_id: Google Calendar event ID
            
        Returns:
            True if successful
        """
        return self.calendar.update_event_status(event_id, "definitief")
    
    def mark_as_proposal(self, event_id: str) -> bool:
        """
        Mark lesson as proposal (change to voorstel)
        
        Args:
            event_id: Google Calendar event ID
            
        Returns:
            True if successful
        """
        return self.calendar.update_event_status(event_id, "voorstel")
    
    def mark_as_trial(self, event_id: str) -> bool:
        """
        Mark lesson as trial (change to proefles)
        
        Args:
            event_id: Google Calendar event ID
            
        Returns:
            True if successful
        """
        return self.calendar.update_event_status(event_id, "proefles")
    
    def mark_as_intake(self, event_id: str) -> bool:
        """
        Mark lesson as intake
        
        Args:
            event_id: Google Calendar event ID
            
        Returns:
            True if successful
        """
        return self.calendar.update_event_status(event_id, "intake")
    
    def mark_as_school_lesson(self, event_id: str) -> bool:
        """
        Mark lesson as school-related
        
        Args:
            event_id: Google Calendar event ID
            
        Returns:
            True if successful
        """
        return self.calendar.update_event_status(event_id, "schoolles")
    
    def mark_as_substitution(self, event_id: str, substitute_teacher: str = "") -> bool:
        """
        Mark lesson as substitution
        
        Args:
            event_id: Google Calendar event ID
            substitute_teacher: Name of substitute teacher
            
        Returns:
            True if successful
        """
        # Note: This would need to update the description as well
        # For now, just update the status
        return self.calendar.update_event_status(event_id, "vervanging")
    
    def mark_as_follow_up(self, event_id: str) -> bool:
        """
        Mark event as follow-up/reminder
        
        Args:
            event_id: Google Calendar event ID
            
        Returns:
            True if successful
        """
        return self.calendar.update_event_status(event_id, "follow-up")
    
    def get_status_workflow(self, current_status: str) -> Dict[str, Any]:
        """
        Get available status transitions for current status
        
        Args:
            current_status: Current status of the event
            
        Returns:
            Dictionary with available transitions and descriptions
        """
        workflows = {
            "voorstel": {
                "next_states": ["definitief", "proefles", "intake"],
                "description": "Lesson proposal - awaiting confirmation",
                "actions": {
                    "definitief": "Confirm lesson (payment received)",
                    "proefles": "Convert to trial lesson",
                    "intake": "Convert to intake session"
                }
            },
            "proefles": {
                "next_states": ["definitief", "voorstel"],
                "description": "Trial lesson scheduled",
                "actions": {
                    "definitief": "Convert to regular lesson",
                    "voorstel": "Convert to proposal"
                }
            },
            "intake": {
                "next_states": ["definitief", "voorstel"],
                "description": "Intake session scheduled",
                "actions": {
                    "definitief": "Convert to regular lesson",
                    "voorstel": "Convert to proposal"
                }
            },
            "definitief": {
                "next_states": ["vervanging", "follow-up"],
                "description": "Confirmed lesson",
                "actions": {
                    "vervanging": "Mark as substitution",
                    "follow-up": "Add follow-up reminder"
                }
            },
            "schoolles": {
                "next_states": ["vervanging", "follow-up"],
                "description": "School-related lesson",
                "actions": {
                    "vervanging": "Mark as substitution",
                    "follow-up": "Add follow-up reminder"
                }
            },
            "vervanging": {
                "next_states": ["definitief"],
                "description": "Substitution lesson",
                "actions": {
                    "definitief": "Mark as completed"
                }
            },
            "follow-up": {
                "next_states": ["definitief", "voorstel"],
                "description": "Follow-up or reminder",
                "actions": {
                    "definitief": "Mark as completed",
                    "voorstel": "Convert to proposal"
                }
            }
        }
        
        return workflows.get(current_status.lower(), {
            "next_states": [],
            "description": "Unknown status",
            "actions": {}
        })
    
    def get_status_summary(self) -> Dict[str, int]:
        """
        Get summary of events by status
        
        Returns:
            Dictionary with status counts
        """
        # This would need to query the calendar for all events
        # and count them by status
        # For now, return empty dict
        return {}
    
    def get_pending_actions(self) -> List[Dict[str, Any]]:
        """
        Get list of events that need action
        
        Returns:
            List of events requiring attention
        """
        # This would query for events that need status updates
        # For now, return empty list
        return []
