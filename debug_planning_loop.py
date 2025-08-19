#!/usr/bin/env python3
"""
Debug Planning Loop

This script helps identify why the bot gets stuck in a loop after selecting a lesson slot
"""

import os
import sys
from datetime import datetime, timedelta

def debug_planning_flow():
    """Debug the planning flow to identify loop issues"""
    print("🔍 Debug Planning Flow")
    print("=" * 50)
    
    # Test scenarios that might cause loops
    scenarios = [
        {
            "name": "Trial lesson slot selection",
            "msg_content": "2024-01-15T17:00:00+02:00",
            "expected_flow": [
                "1. Parse ISO timestamp",
                "2. Book slot",
                "3. Set pending_intent to 'ask_email'",
                "4. Send email request",
                "5. Wait for email response"
            ]
        },
        {
            "name": "Readable slot selection",
            "msg_content": "Mon 15 Jan 17:00–18:00",
            "expected_flow": [
                "1. Parse readable format",
                "2. Convert to ISO timestamp",
                "3. Book slot",
                "4. Set pending_intent to 'ask_email'",
                "5. Send email request"
            ]
        },
        {
            "name": "Invalid slot selection",
            "msg_content": "invalid slot",
            "expected_flow": [
                "1. Detect invalid format",
                "2. Send error message",
                "3. Resend available slots",
                "4. Stay in planning mode"
            ]
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 Scenario {i}: {scenario['name']}")
        print(f"   Input: '{scenario['msg_content']}'")
        print(f"   Expected flow:")
        for step in scenario['expected_flow']:
            print(f"      {step}")
    
    print(f"\n🔧 Potential Loop Causes:")
    print(f"   1. pending_intent not being set correctly")
    print(f"   2. handle_email_request not being called")
    print(f"   3. pending_intent not being cleared after email")
    print(f"   4. Duplicate message processing")
    print(f"   5. Invalid slot format not handled properly")
    
    print(f"\n🎯 Debug Steps:")
    print(f"   1. Check if pending_intent is set to 'ask_email' after slot selection")
    print(f"   2. Verify handle_email_request is called when pending_intent == 'ask_email'")
    print(f"   3. Ensure pending_intent is cleared after email processing")
    print(f"   4. Check for duplicate message processing")
    print(f"   5. Verify slot format parsing works correctly")

def check_message_handling_flow():
    """Check the message handling flow for potential issues"""
    print(f"\n📝 Message Handling Flow Check:")
    print(f"   1. handle_message_created() receives message")
    print(f"   2. Check if bot is disabled")
    print(f"   3. Check pending_intent")
    print(f"   4. Route to appropriate handler")
    print(f"   5. Update last_processed_message")
    
    print(f"\n⚠️ Potential Issues:")
    print(f"   - pending_intent not being checked early enough")
    print(f"   - Duplicate message processing")
    print(f"   - Handler not being called")
    print(f"   - pending_intent not being updated")

if __name__ == "__main__":
    debug_planning_flow()
    check_message_handling_flow()
