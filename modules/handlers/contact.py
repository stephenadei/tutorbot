#!/usr/bin/env python3
"""
Contact Handlers for TutorBot

This module contains contact management handlers and utilities.
"""

from typing import Dict, Any

# Import dependencies
from modules.utils.cw_api import ChatwootAPI
from modules.utils.text_helpers import get_contact_id_from_conversation
from modules.utils.mapping import map_school_level


def create_child_contact(analysis: Dict[str, Any], conversation_id: int, parent_contact_id: int = None) -> int:
    """Create a separate contact for the child when a parent is writing"""
    try:
        # Get the parent contact ID from the conversation if not provided
        if not parent_contact_id:
            parent_contact_id = get_contact_id_from_conversation(conversation_id)
            if not parent_contact_id:
                print("❌ Could not get parent contact ID")
                return None
        
        # Create child contact with comprehensive info
        child_name = analysis.get("learner_name", "Onbekende leerling")
        child_attrs = {
            "language": "nl",
            "segment": "student",
            "is_adult": False,
            "is_student": True,
            "parent_contact_id": str(parent_contact_id),
            "created_by_parent": True,
            "name": child_name
        }
        
        # Add all available child information
        child_fields = [
            "school_level", "topic_primary", "topic_secondary", "goals",
            "preferred_times", "lesson_mode", "toolset", "program", "urgency"
        ]
        
        for field in child_fields:
            if analysis.get(field):
                if field == "school_level":
                    child_attrs[field] = map_school_level(analysis[field])
                else:
                    child_attrs[field] = analysis[field]
        
        # Create the child contact using ChatwootAPI
        # Try different inbox IDs - WhatsApp is usually 1 or 2
        for inbox_id in [1, 2]:
            try:
                child_contact = ChatwootAPI.create_contact(
                    inbox_id=inbox_id,
                    name=child_name,
                    phone="",  # No phone number for now
                    attrs=child_attrs
                )
                if child_contact:
                    break
            except Exception as e:
                print(f"⚠️ Failed to create contact with inbox_id {inbox_id}: {e}")
                continue
        
        if child_contact:
            child_contact_id = child_contact.get("id") or child_contact.get("payload", {}).get("contact", {}).get("id")
            if child_contact_id:
                print(f"👶 Created child contact {child_contact_id} for {child_name}")
                return child_contact_id
            else:
                print(f"❌ No child contact ID in response: {child_contact}")
                return None
        else:
            print("❌ Failed to create child contact")
            return None
            
    except Exception as e:
        print(f"❌ Error creating child contact: {e}")
        return None
