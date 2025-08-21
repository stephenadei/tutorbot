#!/usr/bin/env python3
"""
Test script for language detection and prefill flow
"""

import os
import sys
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main module
import main

def test_language_detection():
    """Test the language detection functionality"""
    print("🧪 Testing Language Detection")
    print("=" * 50)
    
    # Test cases
    test_messages = [
        "Ik ben een VWO 5 leerling en wil bijles wiskunde en natuurkunde online",
        "Hello, I want math tutoring for my daughter",
        "Hallo! Ik zoek bijles voor mijn zoon",
        "I need help with physics homework",
        "Kan ik bijles krijgen voor Engels?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Test {i}: '{message}'")
        
        try:
            # Test language detection
            lang = main.detect_language_from_message(message)
            print(f"   🌍 Detected language: {lang}")
            
            # Test OpenAI analysis
            analysis = main.analyze_first_message_with_openai(message, lang)
            print(f"   🤖 OpenAI analysis: {analysis}")
            
            # Test prefill extraction
            prefill_info = main.prefill_intake_from_message(message, lang)
            print(f"   📋 Prefill info: {prefill_info}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            print(f"   📄 Traceback: {traceback.format_exc()}")

def test_prefill_confirmation():
    """Test the prefill confirmation flow"""
    print("\n🧪 Testing Prefill Confirmation Flow")
    print("=" * 50)
    
    # Mock conversation and contact IDs
    cid = 50
    contact_id = 1
    lang = "nl"
    
    try:
        print(f"📞 Testing with conversation {cid}, contact {contact_id}, language {lang}")
        
        # Test prefill action menu
        print("   🎯 Testing show_prefill_action_menu...")
        main.show_prefill_action_menu(cid, contact_id, lang)
        print("   ✅ show_prefill_action_menu completed")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        print(f"   📄 Traceback: {traceback.format_exc()}")

def test_chatwoot_api():
    """Test Chatwoot API functionality"""
    print("\n🧪 Testing Chatwoot API")
    print("=" * 50)
    
    try:
        from scripts.cw_api import ChatwootAPI
        
        # Test sending a simple message
        cid = 50
        test_message = "🧪 Test message from language detection test"
        
        print(f"📤 Sending test message to conversation {cid}")
        success = ChatwootAPI.send_message(cid, test_message, "text")
        
        if success:
            print("   ✅ Message sent successfully")
        else:
            print("   ❌ Failed to send message")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        print(f"   📄 Traceback: {traceback.format_exc()}")

def main():
    """Run all tests"""
    print("🚀 Starting Language Detection and Prefill Tests")
    print(f"⏰ Time: {datetime.now()}")
    print("=" * 60)
    
    # Test language detection
    test_language_detection()
    
    # Test prefill confirmation
    test_prefill_confirmation()
    
    # Test Chatwoot API
    test_chatwoot_api()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()
