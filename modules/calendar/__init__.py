"""
Google Calendar Integration Module

Handles all calendar operations including:
- Lesson scheduling
- Color coding
- Status management
- Integration with bot workflows
"""

from .calendar_manager import CalendarManager
from .event_creator import EventCreator
from .status_manager import StatusManager

__all__ = ['CalendarManager', 'EventCreator', 'StatusManager']
