"""
Notability Notes Integration Module

Handles all notes operations including:
- Note creation and organization
- Google Drive backup structure
- Integration with calendar events
"""

from .notes_manager import NotesManager
from .drive_backup import DriveBackup
from .note_organizer import NoteOrganizer

__all__ = ['NotesManager', 'DriveBackup', 'NoteOrganizer']
