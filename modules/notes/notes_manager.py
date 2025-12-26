"""
Notes Manager for Notability Integration

Handles note creation, organization, and Google Drive backup
for lesson notes and student documentation.
"""

import os
import tempfile
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class NotesManager:
    """Manages Notability notes and Google Drive backup"""
    
    def __init__(self):
        self.service_account_json = os.getenv("GCAL_SERVICE_ACCOUNT_JSON")
        self.drive_service = None
        self.lessons_folder_id = None
        self._initialize_drive_service()
        
        # Initialize MinIO client for read operations
        try:
            from modules.storage.minio_client import MinIOClient
            self.minio_client = MinIOClient()
            self.minio_bucket = "raw-notability"
        except Exception as e:
            print(f"⚠️  MinIO client not available: {e}")
            self.minio_client = None
    
    def _initialize_drive_service(self):
        """Initialize Google Drive service"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_json,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            self.drive_service = build('drive', 'v3', credentials=credentials)
            print("✅ Google Drive service initialized")
            
            # Find or create the "Lessen" folder
            self.lessons_folder_id = self._get_or_create_lessons_folder()
            
        except Exception as e:
            print(f"❌ Failed to initialize Google Drive service: {e}")
            self.drive_service = None
    
    def _get_or_create_lessons_folder(self) -> Optional[str]:
        """Get or create the main 'Lessen' folder in Google Drive"""
        if not self.drive_service:
            return None
        
        try:
            # Search for existing "Lessen" folder
            query = "name='Lessen' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.drive_service.files().list(q=query).execute()
            files = results.get('files', [])
            
            if files:
                folder_id = files[0]['id']
                print(f"✅ Found existing 'Lessen' folder: {folder_id}")
                return folder_id
            
            # Create new folder if it doesn't exist
            folder_metadata = {
                'name': 'Lessen',
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.drive_service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            print(f"✅ Created new 'Lessen' folder: {folder_id}")
            return folder_id
            
        except Exception as e:
            print(f"❌ Failed to get/create lessons folder: {e}")
            return None
    
    def create_student_folder(self, student_name: str) -> Optional[str]:
        """
        Create a folder for a specific student
        
        Args:
            student_name: Name of the student
            
        Returns:
            Folder ID if successful, None otherwise
        """
        if not self.drive_service or not self.lessons_folder_id:
            return None
        
        try:
            # Check if folder already exists
            query = f"name='{student_name}' and mimeType='application/vnd.google-apps.folder' and '{self.lessons_folder_id}' in parents and trashed=false"
            results = self.drive_service.files().list(q=query).execute()
            files = results.get('files', [])
            
            if files:
                folder_id = files[0]['id']
                print(f"✅ Found existing folder for {student_name}: {folder_id}")
                return folder_id
            
            # Create new student folder
            folder_metadata = {
                'name': student_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [self.lessons_folder_id]
            }
            
            folder = self.drive_service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            print(f"✅ Created folder for {student_name}: {folder_id}")
            return folder_id
            
        except Exception as e:
            print(f"❌ Failed to create student folder: {e}")
            return None
    
    def create_lesson_note(self, 
                          student_name: str,
                          lesson_date: datetime,
                          lesson_topic: str,
                          note_content: str = "",
                          note_file_path: str = "") -> Optional[str]:
        """
        Create a lesson note entry
        
        Args:
            student_name: Name of the student
            lesson_date: Date of the lesson
            lesson_topic: Topic of the lesson
            note_content: Text content of the note
            note_file_path: Path to Notability file (if available)
            
        Returns:
            Note ID if successful, None otherwise
        """
        if not self.drive_service:
            return None
        
        try:
            # Get or create student folder
            student_folder_id = self.create_student_folder(student_name)
            if not student_folder_id:
                return None
            
            # Format filename: YYYY-MM-DD - Student Name - Topic
            date_str = lesson_date.strftime("%Y-%m-%d")
            filename = f"{date_str} - {student_name} - {lesson_topic}"
            
            # Create note content
            note_text = f"""
# {filename}

**Student:** {student_name}
**Date:** {date_str}
**Topic:** {lesson_topic}

## Notes
{note_content}

## Next Steps
- [ ] Follow-up actions
- [ ] Homework assigned
- [ ] Next lesson planned

---
*Created by TutorBot*
            """.strip()
            
            # Create Google Doc
            doc_metadata = {
                'name': filename,
                'mimeType': 'application/vnd.google-apps.document',
                'parents': [student_folder_id]
            }
            
            doc = self.drive_service.files().create(
                body=doc_metadata,
                media_body=None,
                fields='id'
            ).execute()
            
            doc_id = doc.get('id')
            
            # Add content to the document
            # Note: This would require Google Docs API for content insertion
            # For now, we just create the document structure
            
            print(f"✅ Created lesson note: {filename} (ID: {doc_id})")
            return doc_id
            
        except Exception as e:
            print(f"❌ Failed to create lesson note: {e}")
            return None
    
    def get_notes_link(self, student_name: str, lesson_date: datetime = None) -> str:
        """
        Get the Google Drive link for student notes
        
        Args:
            student_name: Name of the student
            lesson_date: Optional specific date
            
        Returns:
            Google Drive link
        """
        if not self.lessons_folder_id:
            return ""
        
        try:
            # Find student folder
            query = f"name='{student_name}' and mimeType='application/vnd.google-apps.folder' and '{self.lessons_folder_id}' in parents and trashed=false"
            results = self.drive_service.files().list(q=query).execute()
            files = results.get('files', [])
            
            if files:
                folder_id = files[0]['id']
                return f"https://drive.google.com/drive/u/0/folders/{folder_id}"
            
            return ""
            
        except Exception as e:
            print(f"❌ Failed to get notes link: {e}")
            return ""
    
    def list_student_notes(self, student_name: str) -> List[Dict[str, Any]]:
        """
        List all notes for a student
        
        Args:
            student_name: Name of the student
            
        Returns:
            List of note files with metadata
        """
        if not self.drive_service:
            return []
        
        try:
            # Get student folder
            student_folder_id = self.create_student_folder(student_name)
            if not student_folder_id:
                return []
            
            # List all files in student folder
            query = f"'{student_folder_id}' in parents and trashed=false"
            results = self.drive_service.files().list(
                q=query,
                fields="files(id,name,createdTime,modifiedTime,mimeType,webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            
            # Sort by creation date (newest first)
            files.sort(key=lambda x: x.get('createdTime', ''), reverse=True)
            
            return files
            
        except Exception as e:
            print(f"❌ Failed to list student notes: {e}")
            return []
    
    def backup_notability_file(self, 
                              student_name: str,
                              file_path: str,
                              lesson_date: datetime,
                              lesson_topic: str) -> Optional[str]:
        """
        Backup a Notability file to Google Drive
        
        Args:
            student_name: Name of the student
            file_path: Path to the Notability file
            lesson_date: Date of the lesson
            lesson_topic: Topic of the lesson
            
        Returns:
            File ID if successful, None otherwise
        """
        if not self.drive_service or not os.path.exists(file_path):
            return None
        
        try:
            # Get or create student folder
            student_folder_id = self.create_student_folder(student_name)
            if not student_folder_id:
                return None
            
            # Format filename
            date_str = lesson_date.strftime("%Y-%m-%d")
            filename = f"{date_str} - {student_name} - {lesson_topic}"
            
            # Upload file
            file_metadata = {
                'name': filename,
                'parents': [student_folder_id]
            }
            
            media = MediaFileUpload(file_path, resumable=True)
            
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            print(f"✅ Backed up Notability file: {filename} (ID: {file_id})")
            return file_id
            
        except Exception as e:
            print(f"❌ Failed to backup Notability file: {e}")
            return None
    
    # ============================================================================
    # MinIO Read-Only Methods
    # ============================================================================
    
    def list_notability_files(self, student_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List Notability files from MinIO data lake
        
        Args:
            student_name: Optional student name to filter files (searches in object names)
            
        Returns:
            List of file information dictionaries with keys:
                - object_name: Full object name/path
                - size: File size in bytes
                - last_modified: Last modification timestamp
                - etag: Object ETag
        """
        if not self.minio_client or not self.minio_client.client:
            print("⚠️  MinIO client not available")
            return []
        
        try:
            # Ensure bucket exists
            if not self.minio_client.ensure_bucket_exists(self.minio_bucket):
                print(f"❌ Bucket {self.minio_bucket} does not exist")
                return []
            
            # List objects with optional prefix filter
            prefix = None
            if student_name:
                # Filter by student name in object path
                # Assuming naming convention: student_name/... or .../student_name/...
                prefix = student_name
            
            objects = self.minio_client.list_objects(self.minio_bucket, prefix=prefix)
            
            # If student_name provided, filter results more strictly
            if student_name:
                objects = [
                    obj for obj in objects
                    if student_name.lower() in obj["object_name"].lower()
                ]
            
            return objects
            
        except Exception as e:
            print(f"❌ Error listing Notability files: {e}")
            return []
    
    def get_notability_file(self, object_name: str, 
                           download_path: Optional[str] = None) -> Optional[str]:
        """
        Download a Notability file from MinIO
        
        Args:
            object_name: Object name/path in the bucket
            download_path: Optional local path to save the file.
                          If None, saves to temporary directory.
            
        Returns:
            Path to downloaded file if successful, None otherwise
        """
        if not self.minio_client or not self.minio_client.client:
            print("⚠️  MinIO client not available")
            return None
        
        try:
            # Ensure bucket exists
            if not self.minio_client.ensure_bucket_exists(self.minio_bucket):
                print(f"❌ Bucket {self.minio_bucket} does not exist")
                return None
            
            # Check if object exists
            if not self.minio_client.object_exists(self.minio_bucket, object_name):
                print(f"❌ Object {object_name} does not exist in bucket")
                return None
            
            # Determine download path
            if not download_path:
                # Create temp file
                temp_dir = tempfile.gettempdir()
                filename = os.path.basename(object_name) or "notability_file"
                download_path = os.path.join(temp_dir, filename)
            
            # Download file
            success = self.minio_client.download_file(
                self.minio_bucket,
                object_name,
                download_path
            )
            
            if success:
                return download_path
            return None
            
        except Exception as e:
            print(f"❌ Error downloading Notability file: {e}")
            return None
    
    def get_notability_file_url(self, object_name: str,
                               expires: timedelta = timedelta(hours=1)) -> Optional[str]:
        """
        Get a presigned URL for direct access to a Notability file
        
        Args:
            object_name: Object name/path in the bucket
            expires: Time until URL expires (default: 1 hour)
            
        Returns:
            Presigned URL if successful, None otherwise
        """
        if not self.minio_client or not self.minio_client.client:
            print("⚠️  MinIO client not available")
            return None
        
        try:
            # Ensure bucket exists
            if not self.minio_client.ensure_bucket_exists(self.minio_bucket):
                print(f"❌ Bucket {self.minio_bucket} does not exist")
                return None
            
            # Check if object exists
            if not self.minio_client.object_exists(self.minio_bucket, object_name):
                print(f"❌ Object {object_name} does not exist in bucket")
                return None
            
            # Generate presigned URL
            url = self.minio_client.get_presigned_url(
                self.minio_bucket,
                object_name,
                expires=expires
            )
            
            return url
            
        except Exception as e:
            print(f"❌ Error generating presigned URL: {e}")
            return None
