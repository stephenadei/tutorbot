"""
Data Exporter for S3 data lake.
Exports conversations and error logs to bronze-communication bucket.
Supports tutoring contract paths with run_id when run_id is provided.
"""
import os
import json
import gzip
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from .minio_client import MinIOClient
from modules.utils.cw_api import ChatwootAPI

# Optional: for run_id path building (contract)
try:
    from ...ingestion_service.scripts.tutoring_contract import bronze_prefix  # noqa
except Exception:
    pass


class DataExporter:
    """Export conversations and error logs to S3 data lake"""
    
    def __init__(self, bucket_name: Optional[str] = None):
        """Initialize data exporter with S3 client (via MinIO SDK)"""
        self.minio_client = MinIOClient()
        # S3 primary: use DATALAKE_BUCKET; legacy: use bronze-communication
        self.bucket_name = bucket_name or os.environ.get("DATALAKE_BUCKET") or "bronze-communication"
        self.cw_api = ChatwootAPI
    
    def ensure_bucket(self) -> bool:
        """Ensure the export bucket exists"""
        return self.minio_client.ensure_bucket_exists(self.bucket_name)
    
    def export_conversations(self, start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None,
                            conversation_ids: Optional[List[int]] = None,
                            run_id: Optional[str] = None) -> bool:
        """
        Export conversations to S3 data lake
        
        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            conversation_ids: Optional list of specific conversation IDs to export
            run_id: Optional run ID for tutoring contract; if set, writes under
                    tutoring/bronze/raw_message_exports/<ingest_date>/run_id=<run_id>/
                    and writes _SUCCESS.json
            
        Returns:
            True if export successful, False otherwise
        """
        if not self.ensure_bucket():
            print("❌ Failed to ensure bucket exists")
            return False
        
        try:
            export_timestamp = datetime.now(timezone.utc)
            date_str = export_timestamp.strftime("%Y-%m-%d")
            time_str = export_timestamp.strftime("%H%M%S")
            
            # Build export data
            export_data = {
                "export_type": "conversations",
                "timestamp": export_timestamp.isoformat().replace("+00:00", "Z"),
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
            
            # Object name: tutoring contract path if run_id set, else legacy
            if run_id is not None:
                base_prefix = f"tutoring/bronze/raw_message_exports/{date_str}/run_id={run_id}"
                object_name = f"{base_prefix}/conversations-{date_str}-{time_str}.json.gz"
            else:
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
                if run_id is not None:
                    self._write_success_marker(base_prefix, run_id, records_count=len(export_data["conversations"]))
            
            return success
            
        except Exception as e:
            print(f"❌ Error exporting conversations: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _write_success_marker(self, base_prefix: str, run_id: str, files_count: Optional[int] = None, records_count: Optional[int] = None) -> None:
        """Write _SUCCESS.json at base_prefix per tutoring contract."""
        payload = {
            "run_id": run_id,
            "completed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "trigger": "manual",
        }
        if files_count is not None:
            payload["files_count"] = files_count
        if records_count is not None:
            payload["records_count"] = records_count
        key = f"{base_prefix}/_SUCCESS.json"
        try:
            self.minio_client.upload_data(
                self.bucket_name,
                key,
                json.dumps(payload, indent=2).encode("utf-8"),
                content_type="application/json",
            )
            print(f"✅ Wrote _SUCCESS.json to {key}")
        except Exception as e:
            print(f"⚠️  Failed to write _SUCCESS.json: {e}")
    
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
        Export error logs to S3 data lake
        
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
        Export a single conversation to S3 data lake
        
        Args:
            conversation_id: ID of the conversation to export
            
        Returns:
            True if export successful, False otherwise
        """
        return self.export_conversations(conversation_ids=[conversation_id])

