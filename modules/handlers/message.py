#!/usr/bin/env python3
"""
Message Handlers for TutorBot

This module contains the main message processing logic.
"""

from typing import Dict, Any
from modules.handlers.conversation import handle_message_created

def process_incoming_message(data: Dict[str, Any]):
    """Process incoming message from webhook"""
    handle_message_created(data)
