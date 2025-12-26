"""
Data Exporter for MinIO data lake.
Exports conversations and error logs to raw-chatwoot bucket.
"""
import os
import json
import gzip
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .minio_client import MinIOClient
from modules.utils.cw_api import ChatwootAPI


class DataExporter:
    """Export conversations and error logs to MinIO data lake"""
    
    def __init__(self):
        """Initialize data exporter with MinIO client"""
        self.minio_client = MinIOClient()
        self.bucket_name = "raw-chatwoot"
        self.cw_api = ChatwootAPI
    
    def ensure_bucket(self) -> bool:
        """Ensure the export bucket exists"""
        return self.minio_client.ensure_bucket_exists(self.bucket_name)
    
    def export_conversations(self, start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None,
                            conversation_ids: Optional[List[int]] = None) -> bool:
        """
        Export conversations to MinIO
        
        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            conversation_ids: Optional list of specific conversation IDs to export
            
        Returns:
            True if export successful, False otherwise
        """
        if not self.ensure_bucket():
            print("❌ Failed to ensure bucket exists")
            return False
        
        try:
            export_timestamp = datetime.utcnow()
            date_str = export_timestamp.strftime("%Y-%m-%d")
            time_str = export_timestamp.strftime("%H%M%S")
            
            # Build export data
            export_data = {
                "export_type": "conversations",
                "timestamp": export_timestamp.isoformat() + "Z",
                "period": {
                    "start": start_date.isoformat() + "Z" if start_date else None,
                    "end": end_date.isoformat() + "Z" if end_date else None
                },
                "conversations": []
            }
            
            # If specific conversation IDs provided, export those
            if conversation_ids:
                for conv_id in conversation_ids:
                    conv = self.cw_api.get_conversation(conv_id)
                    if conv:
                        # Get messages for this conversation
                        messages = self._get_conversation_messages(conv_id)
                        conv_data = {
                            "id": conv.get("id"),
                            "contact_id": conv.get("contact", {}).get("id") if conv.get("contact") else None,
                            "status": conv.get("status"),
                            "created_at": conv.get("created_at"),
                            "updated_at": conv.get("updated_at"),
                            "custom_attributes": conv.get("custom_attributes", {}),
                            "messages": messages
                        }
                        export_data["conversations"].append(conv_data)
            else:
                # Note: Chatwoot API doesn't have a direct "list all conversations" endpoint
                # This would need to be implemented based on your specific needs
                # For now, we'll export conversations that are passed in
                print("⚠️  Bulk conversation export requires conversation_ids parameter")
                return False
            
            # Create object name with date structure
            object_name = f"conversations/{date_str}/conversations-{date_str}-{time_str}.json"
            
            # Compress and upload
            json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
            compressed_data = gzip.compress(json_data.encode('utf-8'))
            
            success = self.minio_client.upload_data(
                self.bucket_name,
                object_name,
                compressed_data,
                content_type="application/json"
            )
            
            if success:
                print(f"✅ Exported {len(export_data['conversations'])} conversations to {object_name}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error exporting conversations: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _get_conversation_messages(self, conversation_id: int) -> List[Dict[str, Any]]:
        """
        Get messages for a conversation
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            List of message dictionaries
        """
        # Get messages from Chatwoot API
        try:
            import requests
            from modules.utils.cw_api import CW_URL, ACC, ADMIN_TOKEN
            
            url = f"{CW_URL}/api/v1/accounts/{ACC}/conversations/{conversation_id}/messages"
            headers = {
                "api_access_token": ADMIN_TOKEN,
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=30, verify=False)
            if response.status_code == 200:
                data = response.json()
                # Handle both direct response and payload wrapper
                if "payload" in data:
                    return data["payload"]
                return data if isinstance(data, list) else []
            return []
        except Exception as e:
            print(f"⚠️  Error fetching messages for conversation {conversation_id}: {e}")
            return []
    
    def export_error_logs(self, error_logs: List[Dict[str, Any]]) -> bool:
        """
        Export error logs to MinIO
        
        Args:
            error_logs: List of error log dictionaries with keys:
                - timestamp: ISO format timestamp
                - level: Error level (ERROR, WARNING, etc.)
                - module: Module name where error occurred
                - message: Error message
                - traceback: Optional traceback string
                
        Returns:
            True if export successful, False otherwise
        """
        if not self.ensure_bucket():
            print("❌ Failed to ensure bucket exists")
            return False
        
        try:
            export_timestamp = datetime.utcnow()
            date_str = export_timestamp.strftime("%Y-%m-%d")
            time_str = export_timestamp.strftime("%H%M%S")
            
            export_data = {
                "export_type": "error_logs",
                "timestamp": export_timestamp.isoformat() + "Z",
                "errors": error_logs
            }
            
            # Create object name with date structure
            object_name = f"error-logs/{date_str}/errors-{date_str}-{time_str}.json"
            
            # Compress and upload
            json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
            compressed_data = gzip.compress(json_data.encode('utf-8'))
            
            success = self.minio_client.upload_data(
                self.bucket_name,
                object_name,
                compressed_data,
                content_type="application/json"
            )
            
            if success:
                print(f"✅ Exported {len(error_logs)} error logs to {object_name}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error exporting error logs: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def export_conversation(self, conversation_id: int) -> bool:
        """
        Export a single conversation to MinIO
        
        Args:
            conversation_id: ID of the conversation to export
            
        Returns:
            True if export successful, False otherwise
        """
        return self.export_conversations(conversation_ids=[conversation_id])

