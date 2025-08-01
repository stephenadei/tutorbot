#!/usr/bin/env python3
"""
Test Script voor TutorBot
Simuleert webhook events om de bot functionaliteit te testen.
"""

import requests
import json
import hmac
import hashlib
import os
from datetime import datetime

# Configuratie
BOT_URL = "http://localhost:8000/cw"
HMAC_SECRET = os.getenv("CW_HMAC_SECRET", "e6cffc2ec52cedc73e616746e629d346ca55daee82d0c87286eca62aa8d71393")

def create_signature(payload: str) -> str:
    """Create HMAC signature for webhook"""
    return hmac.new(
        HMAC_SECRET.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

def send_webhook(event_data: dict) -> bool:
    """Send webhook to bot"""
    payload = json.dumps(event_data)
    signature = create_signature(payload)
    
    headers = {
        "Content-Type": "application/json",
        "X-Chatwoot-Signature": signature
    }
    
    try:
        response = requests.post(BOT_URL, headers=headers, data=payload)
        print(f"📨 Webhook sent: {response.status_code}")
        print(f"📨 Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error sending webhook: {e}")
        return False

def test_conversation_created():
    """Test conversation created event"""
    print("🧪 Testing conversation_created event...")
    
    event_data = {
        "event": "conversation_created",
        "conversation": {
            "id": 12345,
            "status": "open",
            "custom_attributes": {}
        },
        "contact": {
            "id": 67890,
            "name": "Test User",
            "phone_number": "+31612345678",
            "custom_attributes": {}
        }
    }
    
    return send_webhook(event_data)

def test_language_selection():
    """Test language selection"""
    print("🧪 Testing language selection...")
    
    event_data = {
        "event": "message_created",
        "message_type": "incoming",
        "content": "🇳🇱 Nederlands",
        "conversation": {
            "id": 12345,
            "status": "open",
            "custom_attributes": {}
        },
        "sender": {
            "id": 67890,
            "name": "Test User",
            "phone_number": "+31612345678",
            "custom_attributes": {}
        }
    }
    
    return send_webhook(event_data)

def test_new_customer_flow():
    """Test new customer flow"""
    print("🧪 Testing new customer flow...")
    
    # Step 1: Select trial lesson
    event_data = {
        "event": "message_created",
        "message_type": "incoming",
        "content": "🎯 Proefles plannen",
        "conversation": {
            "id": 12345,
            "status": "open",
            "custom_attributes": {}
        },
        "sender": {
            "id": 67890,
            "name": "Test User",
            "phone_number": "+31612345678",
            "custom_attributes": {
                "language": "nl",
                "segment": "new"
            }
        }
    }
    
    if not send_webhook(event_data):
        return False
    
    # Step 2: Select "voor mezelf"
    event_data["content"] = "👤 Voor mezelf"
    if not send_webhook(event_data):
        return False
    
    # Step 3: Age check - Yes
    event_data["content"] = "✅ Ja"
    if not send_webhook(event_data):
        return False
    
    # Step 4: Learner name
    event_data["content"] = "Jan Jansen"
    if not send_webhook(event_data):
        return False
    
    # Step 5: Education level
    event_data["content"] = "HAVO"
    if not send_webhook(event_data):
        return False
    
    # Step 6: Subject
    event_data["content"] = "subject:math"
    if not send_webhook(event_data):
        return False
    
    # Step 7: Goals
    event_data["content"] = "Examen voorbereiding"
    if not send_webhook(event_data):
        return False
    
    # Step 8: Preferred times
    event_data["content"] = "Woensdag en vrijdag middag"
    if not send_webhook(event_data):
        return False
    
    # Step 9: Lesson mode
    event_data["content"] = "online"
    return send_webhook(event_data)

def test_existing_customer_flow():
    """Test existing customer flow"""
    print("🧪 Testing existing customer flow...")
    
    event_data = {
        "event": "message_created",
        "message_type": "incoming",
        "content": "📅 Zelfde vak/voorkeuren",
        "conversation": {
            "id": 12346,
            "status": "open",
            "custom_attributes": {}
        },
        "sender": {
            "id": 67891,
            "name": "Existing User",
            "phone_number": "+31612345679",
            "custom_attributes": {
                "language": "nl",
                "segment": "existing",
                "customer_since": "2024-01-15"
            }
        }
    }
    
    return send_webhook(event_data)

def test_weekend_customer_flow():
    """Test weekend customer flow"""
    print("🧪 Testing weekend customer flow...")
    
    event_data = {
        "event": "conversation_created",
        "conversation": {
            "id": 12347,
            "status": "open",
            "custom_attributes": {}
        },
        "contact": {
            "id": 67892,
            "name": "Weekend User",
            "phone_number": "+31612345680",
            "custom_attributes": {
                "weekend_whitelisted": True
            }
        }
    }
    
    return send_webhook(event_data)

def test_payment_webhook():
    """Test Stripe payment webhook"""
    print("🧪 Testing payment webhook...")
    
    event_data = {
        "id": "evt_test_payment",
        "object": "event",
        "api_version": "2020-08-27",
        "created": int(datetime.now().timestamp()),
        "data": {
            "object": {
                "id": "cs_test_payment",
                "object": "checkout.session",
                "amount_total": 5000,
                "currency": "eur",
                "metadata": {
                    "chatwoot_conversation_id": "12345",
                    "order_id": "SPL-20241201-12345"
                }
            }
        },
        "type": "checkout.session.completed"
    }
    
    # Send to payment webhook endpoint
    try:
        response = requests.post(
            "http://localhost:8000/webhook/payments",
            headers={"Content-Type": "application/json"},
            data=json.dumps(event_data)
        )
        print(f"📨 Payment webhook sent: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error sending payment webhook: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 TutorBot Test Suite")
    print("=" * 50)
    
    tests = [
        ("Conversation Created", test_conversation_created),
        ("Language Selection", test_language_selection),
        ("New Customer Flow", test_new_customer_flow),
        ("Existing Customer Flow", test_existing_customer_flow),
        ("Weekend Customer Flow", test_weekend_customer_flow),
        ("Payment Webhook", test_payment_webhook)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"✅ {test_name}: {'PASS' if result else 'FAIL'}")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main() 