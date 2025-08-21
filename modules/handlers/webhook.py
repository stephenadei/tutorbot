#!/usr/bin/env python3
"""
Webhook Handlers for TutorBot

This module contains the main webhook handlers for Chatwoot integration.
"""

import hashlib
import hmac
from flask import request
from typing import Dict, Any

# Import dependencies
from modules.utils.cw_api import (
    get_contact_attrs, set_contact_attrs, get_conv_attrs, set_conv_attrs,
    add_conv_labels, remove_conv_labels
)
from modules.utils.text_helpers import send_text_with_duplicate_check
from modules.core.config import CW_HMAC_SECRET
from modules.utils.mapping import detect_segment

def verify_webhook(request) -> bool:
    """
    Verify Chatwoot webhook signature using HMAC-SHA256.
    """
    if not CW_HMAC_SECRET:
        # Allow if secret is not configured (development mode)
        print("⚠️ No HMAC secret configured - allowing all requests")
        return True

    signature = request.headers.get('X-Chatwoot-Signature')
    if not signature:
        print("⚠️ No signature found in headers - allowing request (temporary)")
        return True

    try:
        expected = hmac.new(
            CW_HMAC_SECRET.encode(),
            request.get_data(),
            hashlib.sha256
        ).hexdigest()
        is_valid = hmac.compare_digest(signature, expected)
        if not is_valid:
            print(f"⚠️ Signature mismatch - expected: {expected[:10]}..., received: {signature[:10]}...")
        return is_valid
    except Exception as exc:
        print(f"❌ Error verifying webhook signature: {exc}")
        return False

def handle_conversation_created(data: Dict[str, Any]):
    """Handle new conversation creation"""
    conversation = data.get("conversation", {})
    contact = data.get("contact", {})
    
    cid = conversation.get("id")
    contact_id = contact.get("id")
    
    if not cid or not contact_id:
        print("❌ Missing conversation_id or contact_id")
        return
    
    print(f"🆕 New conversation - Conv:{cid} Contact:{contact_id}")
    
    # Initialize conversation attributes
    set_conv_attrs(cid, {
        "language_prompted": False,
        "intake_completed": False,
        "order_id": None
    })
    
    # Detect segment and set contact attribute
    segment = detect_segment(contact_id)
    set_contact_attrs(contact_id, {"segment": segment})
    print(f"🏷️ Segment detected: {segment}")
    
    # Check if language needs to be prompted
    contact_attrs = get_contact_attrs(contact_id)
    if not contact_attrs.get("language") and not get_conv_attrs(cid).get("language_prompted"):
        # Don't prompt for language immediately - wait for first message
        # This allows prefill to run first
        print(f"🌍 Waiting for first message before language selection")
    else:
        print(f"🌍 Language already set or prompted")

def handle_message_created(data: Dict[str, Any]):
    """Handle incoming message creation"""
    # This is the main message processing function
    # It will be implemented in the main message handler module
    from modules.handlers.message import process_incoming_message
    process_incoming_message(data)

def process_webhook(data: Dict[str, Any]) -> str:
    """
    Main webhook processing function.
    
    Args:
        data: Webhook data from Chatwoot
    
    Returns:
        str: Response message
    """
    event = data.get("event")
    msg_type = data.get("message_type")
    conversation_id = data.get("conversation", {}).get("id", "unknown")
    contact_id = data.get("contact", {}).get("id") or data.get("sender", {}).get("id", "unknown")
    content = data.get("content", "")
    message_content = content[:50] + "..." if content and len(content) > 50 else content or ""
    event_str = event.upper() if event else "UNKNOWN"
    
    # Create a unique webhook ID for idempotency
    message_id = data.get("id") or data.get("message", {}).get("id")
    webhook_id = f"{conversation_id}_{message_id}_{event}"
    
    # Check if we've already processed this exact webhook
    webhook_hash = hashlib.md5(webhook_id.encode()).hexdigest()
    
    # Use a simple in-memory cache for webhook deduplication
    if not hasattr(process_webhook, 'processed_webhooks'):
        process_webhook.processed_webhooks = set()
    
    if webhook_hash in process_webhook.processed_webhooks:
        print(f"🔄 Duplicate webhook detected: {webhook_id} - skipping")
        return "OK"
    
    # Add to processed set (keep last 1000 webhooks)
    process_webhook.processed_webhooks.add(webhook_hash)
    if len(process_webhook.processed_webhooks) > 1000:
        process_webhook.processed_webhooks.clear()  # Reset to prevent memory leaks

    # Log all webhook events for debugging
    print(f"📨 Webhook received: {event_str} | Type: {msg_type} | Conv:{conversation_id} | Contact:{contact_id} | ID:{message_id}")

    # Handle different event types
    if event == "conversation_created":
        handle_conversation_created(data)
    elif event == "message_created":
        if msg_type == "incoming":
            print(f"💬 [USER IN] Conv:{conversation_id} Contact:{contact_id} | {message_content}")
            handle_message_created(data)
        elif msg_type == "outgoing":
            print(f"🤖 [BOT OUT] Conv:{conversation_id} Contact:{contact_id} | {message_content}")
        else:
            print(f"⏭️ Skipping event: {event_str} type: {msg_type}")
    else:
        print(f"⏭️ Skipping event: {event_str} type: {msg_type}")
    
    return "OK"
