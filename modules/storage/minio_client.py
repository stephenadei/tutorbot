"""
MinIO Client wrapper for data lake operations.
Handles connection, bucket creation, and file operations.
"""
import os
import io
from typing import Optional, List, Dict, Any
from datetime import timedelta
from minio import Minio
from minio.error import S3Error
from minio.commonconfig import REPLACE
from minio.deleteobjects import DeleteObject


class MinIOClient:
    """MinIO client wrapper for data lake operations"""
    
    def __init__(self):
        """Initialize MinIO client with configuration from environment variables"""
        self.endpoint = os.environ.get("MINIO_ENDPOINT", "http://localhost:9000")
        self.access_key = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
        self.secure = os.environ.get("MINIO_SECURE", "false").lower() == "true"
        
        # Remove http:// or https:// from endpoint for MinIO client
        endpoint_url = self.endpoint.replace("http://", "").replace("https://", "")
        
        try:
            self.client = Minio(
                endpoint_url,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )
            print(f"✅ MinIO client initialized: {self.endpoint}")
        except Exception as e:
            print(f"❌ Failed to initialize MinIO client: {e}")
            self.client = None
    
    def ensure_bucket_exists(self, bucket_name: str) -> bool:
        """
        Ensure bucket exists, create if it doesn't
        
        Args:
            bucket_name: Name of the bucket
            
        Returns:
            True if bucket exists or was created, False otherwise
        """
        if not self.client:
            return False
            
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                print(f"✅ Created bucket: {bucket_name}")
            return True
        except S3Error as e:
            print(f"❌ Error ensuring bucket exists: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error ensuring bucket exists: {e}")
            return False
    
    def upload_file(self, bucket_name: str, object_name: str, file_path: str, 
                   content_type: Optional[str] = None) -> bool:
        """
        Upload a file to MinIO bucket
        
        Args:
            bucket_name: Name of the bucket
            object_name: Object name in the bucket
            file_path: Path to the file to upload
            content_type: Optional content type (e.g., 'application/json')
            
        Returns:
            True if upload successful, False otherwise
        """
        if not self.client:
            return False
            
        try:
            self.ensure_bucket_exists(bucket_name)
            
            from minio.commonconfig import Tags
            self.client.fput_object(
                bucket_name,
                object_name,
                file_path,
                content_type=content_type
            )
            print(f"✅ Uploaded {file_path} to {bucket_name}/{object_name}")
            return True
        except S3Error as e:
            print(f"❌ Error uploading file: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error uploading file: {e}")
            return False
    
    def upload_data(self, bucket_name: str, object_name: str, data: bytes,
                   content_type: Optional[str] = None) -> bool:
        """
        Upload data (bytes) to MinIO bucket
        
        Args:
            bucket_name: Name of the bucket
            object_name: Object name in the bucket
            data: Data bytes to upload
            content_type: Optional content type (e.g., 'application/json')
            
        Returns:
            True if upload successful, False otherwise
        """
        if not self.client:
            return False
            
        try:
            self.ensure_bucket_exists(bucket_name)
            
            data_stream = io.BytesIO(data)
            self.client.put_object(
                bucket_name,
                object_name,
                data_stream,
                length=len(data),
                content_type=content_type or "application/octet-stream"
            )
            print(f"✅ Uploaded data to {bucket_name}/{object_name}")
            return True
        except S3Error as e:
            print(f"❌ Error uploading data: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error uploading data: {e}")
            return False
    
    def download_file(self, bucket_name: str, object_name: str, 
                     file_path: str) -> bool:
        """
        Download a file from MinIO bucket
        
        Args:
            bucket_name: Name of the bucket
            object_name: Object name in the bucket
            file_path: Local path to save the file
            
        Returns:
            True if download successful, False otherwise
        """
        if not self.client:
            return False
            
        try:
            self.client.fget_object(bucket_name, object_name, file_path)
            print(f"✅ Downloaded {bucket_name}/{object_name} to {file_path}")
            return True
        except S3Error as e:
            print(f"❌ Error downloading file: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error downloading file: {e}")
            return False
    
    def download_data(self, bucket_name: str, object_name: str) -> Optional[bytes]:
        """
        Download data from MinIO bucket as bytes
        
        Args:
            bucket_name: Name of the bucket
            object_name: Object name in the bucket
            
        Returns:
            Data bytes if successful, None otherwise
        """
        if not self.client:
            return None
            
        try:
            response = self.client.get_object(bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            print(f"❌ Error downloading data: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error downloading data: {e}")
            return None
    
    def list_objects(self, bucket_name: str, prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List objects in a bucket
        
        Args:
            bucket_name: Name of the bucket
            prefix: Optional prefix to filter objects
            
        Returns:
            List of object information dictionaries
        """
        if not self.client:
            return []
            
        try:
            objects = []
            for obj in self.client.list_objects(bucket_name, prefix=prefix, recursive=True):
                objects.append({
                    "object_name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified,
                    "etag": obj.etag
                })
            return objects
        except S3Error as e:
            print(f"❌ Error listing objects: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error listing objects: {e}")
            return []
    
    def get_presigned_url(self, bucket_name: str, object_name: str,
                         expires: timedelta = timedelta(hours=1)) -> Optional[str]:
        """
        Generate a presigned URL for temporary access to an object
        
        Args:
            bucket_name: Name of the bucket
            object_name: Object name in the bucket
            expires: Time until URL expires (default: 1 hour)
            
        Returns:
            Presigned URL if successful, None otherwise
        """
        if not self.client:
            return None
            
        try:
            url = self.client.presigned_get_object(bucket_name, object_name, expires=expires)
            return url
        except S3Error as e:
            print(f"❌ Error generating presigned URL: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error generating presigned URL: {e}")
            return None
    
    def object_exists(self, bucket_name: str, object_name: str) -> bool:
        """
        Check if an object exists in a bucket
        
        Args:
            bucket_name: Name of the bucket
            object_name: Object name in the bucket
            
        Returns:
            True if object exists, False otherwise
        """
        if not self.client:
            return False
            
        try:
            self.client.stat_object(bucket_name, object_name)
            return True
        except S3Error:
            return False
        except Exception:
            return False

