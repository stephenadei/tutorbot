#!/usr/bin/env python3
"""
Payment Handlers for TutorBot

This module contains payment handlers and utilities.
"""

from typing import Dict, Any
import hmac
import hashlib
from datetime import datetime

# Import dependencies
from modules.utils.cw_api import (
    get_contact_attrs, set_contact_attrs, get_conv_attrs, set_conv_attrs
)
from modules.utils.text_helpers import (
    send_text_with_duplicate_check, t, send_admin_warning
)
from modules.core.config import (
    STRIPE_WEBHOOK_SECRET,
    CW_URL,
    CW_ACC_ID,
    CW_ADMIN_TOKEN,
    TZ,
)

def handle_payment_success(event):
    """Handle payment success - moved from main.py"""
    print(f"💳 Processing payment success event")
    
    # Extract payment data
    payment_intent = event.get("data", {}).get("object", {})
    metadata = payment_intent.get("metadata", {})
    
    conversation_id = metadata.get("conversation_id")
    contact_id = metadata.get("contact_id")
    
    if not conversation_id or not contact_id:
        print(f"❌ Missing conversation_id or contact_id in payment metadata")
        return
    
    print(f"💳 Payment success for conversation {conversation_id}")
    
    # Update conversation attributes
    set_conv_attrs(conversation_id, {
        "payment_completed": True,
        "payment_intent_id": payment_intent.get("id"),
        "payment_amount": payment_intent.get("amount"),
        "payment_currency": payment_intent.get("currency")
    })

    # Update contact attributes
    set_contact_attrs(contact_id, {
        "has_paid_lesson": True,
        "has_completed_intake": True,
        "lesson_booked": True,
        "customer_since": datetime.now(TZ).isoformat()
    })

    # Send confirmation message
    send_text_with_duplicate_check(conversation_id, t("payment_success_message", "nl"))

    print(f"✅ Payment success processed successfully")

def create_payment_link(segment, minutes, order_id, conversation_id, student_name, service, audience, program):
    """Create payment link - moved from main.py"""
    print(f"💳 Creating payment link")
    
    # TODO: Implement payment link creation
    # This would integrate with Stripe or another payment provider
    
    payment_link = "https://example.com/payment"  # Placeholder
    
    print(f"💳 Payment link created: {payment_link}")
    return payment_link

def verify_stripe_webhook(payload, signature):
    """Verify Stripe webhook HMAC using configured secret."""
    if not STRIPE_WEBHOOK_SECRET:
        return True
    try:
        expected = hmac.new(
            STRIPE_WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected)
    except Exception:
        return False

def add_payment_note(conversation_id: str, amount_cents: int, currency: str, order_id: str | None = None) -> None:
    """Add a payment note to the conversation in Chatwoot."""
    try:
        url = f"{CW_URL}/api/v1/accounts/{CW_ACC_ID}/conversations/{conversation_id}/notes"
        headers = {"api_access_token": CW_ADMIN_TOKEN, "Content-Type": "application/json"}
        note_text = f"Payment received: {amount_cents/100} {currency.upper()}\nOrder ID: {order_id or ''}"
        import requests
        requests.post(url, headers=headers, json={"content": note_text})
    except Exception:
        pass
