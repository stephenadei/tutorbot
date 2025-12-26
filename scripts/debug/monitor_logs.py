#!/usr/bin/env python3
"""
Monitor TutorBot logs for incoming WhatsApp messages
"""

import os
import sys
import time
import subprocess
from datetime import datetime

def ensure_project_root():
    """Ensure we're running from the project root directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    if os.getcwd() != project_root:
        print(f"🔄 Changing to project root: {project_root}")
        os.chdir(project_root)
    
    return project_root

# Ensure we're in the right directory
PROJECT_ROOT = ensure_project_root()

def check_tutorbot_status():
    """Check if TutorBot is running"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'gunicorn' in result.stdout and 'main:app' in result.stdout:
            return True
    except:
        pass
    return False

def monitor_logs():
    """Monitor logs for webhook activity"""
    print("🔍 Monitoring TutorBot logs for WhatsApp messages...")
    print("   Press Ctrl+C to stop monitoring")
    print("   Send a WhatsApp message to test the webhook")
    print("=" * 60)
    
    # Check if TutorBot is running
    if not check_tutorbot_status():
        print("❌ TutorBot is not running!")
        print("💡 Start it with: sudo gunicorn --bind 0.0.0.0:8000 main:app")
        return
    
    print("✅ TutorBot is running")
    
    # Monitor system logs for webhook activity
    try:
        # Use journalctl to monitor logs
        cmd = ['sudo', 'journalctl', '-f', '-u', 'gunicorn']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print(f"📊 Started monitoring at {datetime.now().strftime('%H:%M:%S')}")
        print("   Waiting for webhook activity...")
        
        while True:
            line = process.stdout.readline()
            if line:
                # Filter for webhook-related messages
                if any(keyword in line.lower() for keyword in ['webhook', 'whatsapp', 'message', 'conv:', 'contact:']):
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"[{timestamp}] {line.strip()}")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped")
        if process:
            process.terminate()
    except Exception as e:
        print(f"❌ Error monitoring logs: {e}")

def test_webhook():
    """Test webhook with a sample message"""
    print("🧪 Testing webhook with sample message...")
    
    test_data = {
        "event": "message_created",
        "message_type": "incoming",
        "conversation": {"id": 999},
        "contact": {"id": 888},
        "content": "TEST MESSAGE - Webhook test",
        "id": "test_123"
    }
    
    try:
        import requests
        response = requests.post(
            "http://localhost:8000/cw",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Webhook test successful!")
            print("   This means TutorBot is working correctly")
            print("   The issue is likely in Chatwoot webhook configuration")
        else:
            print(f"❌ Webhook test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Webhook test error: {e}")

def main():
    """Main function"""
    print("📱 WhatsApp Webhook Monitor")
    print("=" * 40)
    
    # Check TutorBot status
    if not check_tutorbot_status():
        print("❌ TutorBot is not running!")
        print("💡 Start it with:")
        print("   cd /home/stephen/projects/tutorbot")
        print("   export CW_URL='https://crm.stephenadei.nl'")
        print("   export CW_ACC_ID='1'")
        print("   export CW_ADMIN_TOKEN='your_admin_token_here'")
        print("   sudo -E gunicorn --bind 0.0.0.0:8000 main:app")
        return
    
    print("✅ TutorBot is running")
    
    # Test webhook
    test_webhook()
    
    print("\n📋 Troubleshooting steps:")
    print("1. Make sure webhook is configured in Chatwoot:")
    print("   - URL: http://144.91.127.229:8000/cw")
    print("   - Subscriptions: message_created, conversation_created")
    print("   - Status: Enabled")
    print()
    print("2. Send a WhatsApp message to test")
    print()
    print("3. Monitor logs below for activity:")
    print()
    
    # Start monitoring
    monitor_logs()

if __name__ == "__main__":
    main()
