#!/usr/bin/env python3
"""
Log Analysis Script voor TutorBot
Helpt bij het analyseren en filteren van bot logs.
"""

import subprocess
import re
from datetime import datetime
import sys

def get_logs(lines=100):
    """Get recent logs from Docker"""
    try:
        result = subprocess.run(
            ["docker-compose", "logs", "--tail", str(lines), "tutorbot"],
            capture_output=True,
            text=True,
            cwd="."
        )
        return result.stdout
    except Exception as e:
        print(f"❌ Error getting logs: {e}")
        return ""

def filter_logs(logs, filters=None):
    """Filter logs based on criteria"""
    if not filters:
        return logs
    
    filtered_lines = []
    for line in logs.split('\n'):
        if any(filter_text.lower() in line.lower() for filter_text in filters):
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)

def analyze_conversation_flow(logs):
    """Analyze conversation flow patterns"""
    print("🔍 Analyzing conversation flow...")
    
    # Extract conversation patterns
    conversations = {}
    current_conv = None
    
    for line in logs.split('\n'):
        # Find conversation IDs
        conv_match = re.search(r'Conv:(\d+)', line)
        if conv_match:
            conv_id = conv_match.group(1)
            if conv_id not in conversations:
                conversations[conv_id] = []
            current_conv = conv_id
        
        # Add relevant events to conversation
        if current_conv and any(keyword in line for keyword in ['🔔', '💬', '📋', '🎯', '📅', '✅', '❌']):
            conversations[current_conv].append(line.strip())
    
    # Analyze each conversation
    for conv_id, events in conversations.items():
        if len(events) > 1:  # Only show conversations with multiple events
            print(f"\n📊 Conversation {conv_id}:")
            for event in events:
                print(f"  {event}")

def show_summary(logs):
    """Show summary statistics"""
    print("📈 Log Summary:")
    
    # Count different event types
    event_counts = {
        'conversation_created': len(re.findall(r'CONVERSATION_CREATED', logs)),
        'message_created': len(re.findall(r'MESSAGE_CREATED', logs)),
        'text_sent': len(re.findall(r'✅ Text message sent', logs)),
        'quick_replies_sent': len(re.findall(r'✅ Quick replies sent', logs)),
        'errors': len(re.findall(r'❌|⚠️', logs)),
        'intake_steps': len(re.findall(r'📋', logs)),
        'planning': len(re.findall(r'📅', logs)),
        'segments': len(re.findall(r'🏷️ Segment detected', logs))
    }
    
    for event, count in event_counts.items():
        if count > 0:
            print(f"  {event}: {count}")

def show_recent_errors(logs, lines=10):
    """Show recent errors"""
    error_lines = []
    for line in logs.split('\n'):
        if '❌' in line or '⚠️' in line:
            error_lines.append(line.strip())
    
    if error_lines:
        print(f"\n❌ Recent Errors (last {lines}):")
        for error in error_lines[-lines:]:
            print(f"  {error}")
    else:
        print("\n✅ No recent errors found")

def show_segment_distribution(logs):
    """Show segment distribution"""
    segments = {}
    for line in logs.split('\n'):
        match = re.search(r'🏷️ Segment detected: (\w+)', line)
        if match:
            segment = match.group(1)
            segments[segment] = segments.get(segment, 0) + 1
    
    if segments:
        print(f"\n🏷️ Segment Distribution:")
        for segment, count in segments.items():
            print(f"  {segment}: {count}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("🔍 TutorBot Log Analyzer")
        print("=" * 50)
        print("Usage:")
        print("  python3 analyze_logs.py [command] [options]")
        print("\nCommands:")
        print("  summary          - Show log summary")
        print("  errors           - Show recent errors")
        print("  segments         - Show segment distribution")
        print("  flow             - Analyze conversation flow")
        print("  filter <text>    - Filter logs by text")
        print("  raw [lines]      - Show raw logs (default: 50)")
        return
    
    command = sys.argv[1]
    
    # Get logs
    lines = 100
    if command == "raw" and len(sys.argv) > 2:
        lines = int(sys.argv[2])
    
    logs = get_logs(lines)
    if not logs:
        print("❌ No logs found")
        return
    
    # Execute command
    if command == "summary":
        show_summary(logs)
    elif command == "errors":
        show_recent_errors(logs)
    elif command == "segments":
        show_segment_distribution(logs)
    elif command == "flow":
        analyze_conversation_flow(logs)
    elif command == "filter":
        if len(sys.argv) < 3:
            print("❌ Please provide filter text")
            return
        filter_text = sys.argv[2]
        filtered = filter_logs(logs, [filter_text])
        print(f"🔍 Filtered logs for '{filter_text}':")
        print(filtered)
    elif command == "raw":
        print(logs)
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main() 