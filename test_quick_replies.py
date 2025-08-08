#!/usr/bin/env python3
"""
Test script for quick_replies functionality
"""

import os
import sys
import requests

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the function
from main import send_quick_replies, t

def test_quick_replies():
    """Test the quick_replies function"""
    
    # Test conversation ID (you'll need to replace this with a real one)
    conversation_id = 1  # Replace with actual conversation ID
    
    # Test menu options
    menu_title = t("prefill_action_menu_title", "nl")
    menu_options = [
        (t("prefill_action_trial_lesson", "nl"), "plan_trial_lesson"),
        (t("prefill_action_main_menu", "nl"), "go_to_main_menu"),
        (t("prefill_action_handoff", "nl"), "handoff")
    ]
    
    print(f"🎯 Testing quick_replies function")
    print(f"   Title: {menu_title}")
    print(f"   Options: {menu_options}")
    
    # Test the function
    result = send_quick_replies(conversation_id, menu_title, menu_options)
    
    print(f"   Result: {result}")
    
    if result:
        print("✅ Quick replies test successful")
    else:
        print("❌ Quick replies test failed")

if __name__ == "__main__":
    test_quick_replies()
