"""
Google Drive Backup Module

Handles automatic backup of Notability files to Google Drive
with proper organization and metadata.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class DriveBackup:
    """Handles Google Drive backup operations"""
    
    def __init__(self, notes_manager):
        self.notes_manager = notes_manager
        self.drive_service = notes_manager.drive_service
    
    def setup_automatic_backup(self, student_name: str) -> bool:
        """
        Setup automatic backup for a student
        
        Args:
            student_name: Name of the student
            
        Returns:
            True if successful
        """
        try:
            # Create student folder if it doesn't exist
            folder_id = self.notes_manager.create_student_folder(student_name)
            if not folder_id:
                return False
            
            print(f"✅ Automatic backup setup for {student_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup automatic backup: {e}")
            return False
    
    def backup_lesson_files(self, 
                           student_name: str,
                           lesson_date: datetime,
                           lesson_topic: str,
                           file_paths: List[str]) -> List[str]:
        """
        Backup multiple lesson files
        
        Args:
            student_name: Name of the student
            lesson_date: Date of the lesson
            lesson_topic: Topic of the lesson
            file_paths: List of file paths to backup
            
        Returns:
            List of successful file IDs
        """
        successful_backups = []
        
        for file_path in file_paths:
            if os.path.exists(file_path):
                file_id = self.notes_manager.backup_notability_file(
                    student_name, file_path, lesson_date, lesson_topic
                )
                if file_id:
                    successful_backups.append(file_id)
        
        return successful_backups
    
    def get_backup_status(self, student_name: str) -> Dict[str, Any]:
        """
        Get backup status for a student
        
        Args:
            student_name: Name of the student
            
        Returns:
            Dictionary with backup status information
        """
        try:
            notes = self.notes_manager.list_student_notes(student_name)
            
            status = {
                'student_name': student_name,
                'total_notes': len(notes),
                'last_backup': None,
                'folder_link': self.notes_manager.get_notes_link(student_name),
                'recent_notes': notes[:5] if notes else []
            }
            
            if notes:
                # Get the most recent note
                latest_note = notes[0]
                status['last_backup'] = latest_note.get('createdTime')
            
            return status
            
        except Exception as e:
            print(f"❌ Failed to get backup status: {e}")
            return {
                'student_name': student_name,
                'total_notes': 0,
                'last_backup': None,
                'folder_link': "",
                'recent_notes': []
            }
    
    def cleanup_old_backups(self, days_to_keep: int = 365) -> int:
        """
        Clean up old backup files
        
        Args:
            days_to_keep: Number of days to keep backups
            
        Returns:
            Number of files cleaned up
        """
        if not self.drive_service:
            return 0
        
        try:
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Find old files in the lessons folder
            query = f"'{self.notes_manager.lessons_folder_id}' in parents and createdTime < '{cutoff_date.isoformat()}' and trashed=false"
            results = self.drive_service.files().list(q=query).execute()
            old_files = results.get('files', [])
            
            cleaned_count = 0
            for file in old_files:
                try:
                    # Move to trash instead of permanent deletion
                    self.drive_service.files().update(
                        fileId=file['id'],
                        body={'trashed': True}
                    ).execute()
                    cleaned_count += 1
                    print(f"🗑️ Cleaned up old file: {file['name']}")
                except Exception as e:
                    print(f"❌ Failed to clean up file {file['name']}: {e}")
            
            print(f"✅ Cleaned up {cleaned_count} old backup files")
            return cleaned_count
            
        except Exception as e:
            print(f"❌ Failed to cleanup old backups: {e}")
            return 0
    
    def sync_notability_folder(self, notability_folder_path: str) -> Dict[str, Any]:
        """
        Sync a local Notability folder to Google Drive
        
        Args:
            notability_folder_path: Path to local Notability folder
            
        Returns:
            Dictionary with sync results
        """
        if not os.path.exists(notability_folder_path):
            return {'error': 'Folder not found'}
        
        results = {
            'total_files': 0,
            'synced_files': 0,
            'errors': [],
            'synced_files_list': []
        }
        
        try:
            # Walk through the folder structure
            for root, dirs, files in os.walk(notability_folder_path):
                for file in files:
                    results['total_files'] += 1
                    
                    file_path = os.path.join(root, file)
                    
                    # Try to extract student name and date from filename
                    # This is a simplified approach - you might need more sophisticated parsing
                    student_name = self._extract_student_name(file)
                    lesson_date = self._extract_lesson_date(file)
                    
                    if student_name and lesson_date:
                        file_id = self.notes_manager.backup_notability_file(
                            student_name, file_path, lesson_date, "Auto-synced"
                        )
                        
                        if file_id:
                            results['synced_files'] += 1
                            results['synced_files_list'].append({
                                'file': file,
                                'student': student_name,
                                'date': lesson_date.isoformat(),
                                'file_id': file_id
                            })
                        else:
                            results['errors'].append(f"Failed to backup: {file}")
                    else:
                        results['errors'].append(f"Could not parse: {file}")
            
            print(f"✅ Sync completed: {results['synced_files']}/{results['total_files']} files")
            return results
            
        except Exception as e:
            results['errors'].append(f"Sync failed: {str(e)}")
            return results
    
    def _extract_student_name(self, filename: str) -> Optional[str]:
        """Extract student name from filename"""
        # This is a simplified approach
        # You might need more sophisticated parsing based on your naming convention
        parts = filename.split(' - ')
        if len(parts) >= 2:
            return parts[1]  # Assume format: DATE - STUDENT - TOPIC
        return None
    
    def _extract_lesson_date(self, filename: str) -> Optional[datetime]:
        """Extract lesson date from filename"""
        try:
            # Assume format: YYYY-MM-DD - STUDENT - TOPIC
            date_part = filename.split(' - ')[0]
            return datetime.strptime(date_part, "%Y-%m-%d")
        except:
            return None
