#!/usr/bin/env python3
"""
Simple test for language detection issue
"""

import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_language_detection():
    """Test language detection with simple logic"""
    print("🧪 Testing Language Detection Logic")
    print("=" * 50)
    
    test_messages = [
        "Ik ben een VWO 5 leerling en wil bijles wiskunde en natuurkunde online",
        "Hello, I want math tutoring for my daughter",
        "Hallo! Ik zoek bijles voor mijn zoon",
        "I need help with physics homework",
        "Kan ik bijles krijgen voor Engels?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Test {i}: '{message}'")
        
        # Simple language detection logic
        dutch_words = ['ik', 'ben', 'wil', 'bijles', 'wiskunde', 'natuurkunde', 'online', 'hallo', 'zoek', 'voor', 'mijn', 'zoon', 'kan', 'krijgen', 'engels', 'leerling', 'vwo']
        english_words = ['hello', 'want', 'math', 'tutoring', 'daughter', 'need', 'help', 'physics', 'homework']
        
        message_lower = message.lower()
        dutch_count = sum(1 for word in dutch_words if word in message_lower)
        english_count = sum(1 for word in english_words if word in message_lower)
        
        if dutch_count > english_count:
            detected_lang = "nl"
        elif english_count > dutch_count:
            detected_lang = "en"
        else:
            detected_lang = "nl"  # Default to Dutch
            
        print(f"   🌍 Detected language: {detected_lang}")
        print(f"   📊 Dutch words: {dutch_count}, English words: {english_count}")
        
        # Check for specific patterns
        if 'vwo' in message_lower or 'havo' in message_lower or 'vmbo' in message_lower:
            print(f"   🎓 School level detected: {message_lower.split('vwo')[0].split('havo')[0].split('vmbo')[0] if any(x in message_lower for x in ['vwo', 'havo', 'vmbo']) else 'None'}")
        
        if 'wiskunde' in message_lower or 'math' in message_lower:
            print(f"   📐 Math subject detected")
            
        if 'natuurkunde' in message_lower or 'physics' in message_lower:
            print(f"   ⚛️ Physics subject detected")

def test_chatwoot_connection():
    """Test Chatwoot API connection"""
    print("\n🧪 Testing Chatwoot API Connection")
    print("=" * 50)
    
    try:
        from scripts.cw_api import ChatwootAPI
        
        # Test getting contact attributes
        contact_id = 1
        print(f"📞 Testing contact {contact_id} attributes...")
        
        attrs = ChatwootAPI.get_contact_attrs(contact_id)
        print(f"   ✅ Contact attributes: {attrs}")
        
        # Test getting conversation attributes
        conv_id = 50
        print(f"💬 Testing conversation {conv_id} attributes...")
        
        conv_attrs = ChatwootAPI.get_conv_attrs(conv_id)
        print(f"   ✅ Conversation attributes: {conv_attrs}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        print(f"   📄 Traceback: {traceback.format_exc()}")

def main():
    """Run tests"""
    print("🚀 Starting Simple Language Detection Test")
    print("=" * 60)
    
    test_language_detection()
    test_chatwoot_connection()
    
    print("\n✅ Tests completed!")

if __name__ == "__main__":
    main()
