#!/usr/bin/env python3
"""
Script to export conversations and error logs to MinIO data lake

Usage:
    python scripts/data/export_to_datalake.py --conversations [conversation_ids]
    python scripts/data/export_to_datalake.py --error-logs
    python scripts/data/export_to_datalake.py --all
"""
import sys
import os
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import after path setup
from modules.storage.data_exporter import DataExporter


def export_conversations(conversation_ids=None):
    """Export conversations to data lake"""
    exporter = DataExporter()
    
    if conversation_ids:
        # Export specific conversations
        ids = [int(id) for id in conversation_ids.split(',')]
        success = exporter.export_conversations(conversation_ids=ids)
    else:
        print("⚠️  No conversation IDs provided. Use --conversation-ids to specify.")
        return False
    
    return success


def export_error_logs():
    """Export error logs to data lake"""
    exporter = DataExporter()
    
    # Collect error logs from application
    # This is a placeholder - you would collect actual error logs from your logging system
    error_logs = [
        {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": "INFO",
            "module": "export_script",
            "message": "Manual export triggered",
            "traceback": None
        }
    ]
    
    # In a real implementation, you would collect errors from:
    # - Application logs
    # - Error tracking system
    # - Webhook error logs
    # etc.
    
    success = exporter.export_error_logs(error_logs)
    return success


def main():
    parser = argparse.ArgumentParser(description='Export data to MinIO data lake')
    parser.add_argument('--conversations', action='store_true',
                       help='Export conversations')
    parser.add_argument('--conversation-ids', type=str,
                       help='Comma-separated list of conversation IDs to export')
    parser.add_argument('--error-logs', action='store_true',
                       help='Export error logs')
    parser.add_argument('--all', action='store_true',
                       help='Export all data types')
    
    args = parser.parse_args()
    
    if args.all:
        print("📤 Exporting all data to data lake...")
        export_conversations(args.conversation_ids)
        export_error_logs()
    elif args.conversations:
        print("📤 Exporting conversations to data lake...")
        export_conversations(args.conversation_ids)
    elif args.error_logs:
        print("📤 Exporting error logs to data lake...")
        export_error_logs()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

