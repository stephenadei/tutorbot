#!/usr/bin/env python3
"""
Chatwoot Custom Attributes & Labels Audit Script
===============================================

This script audits all custom attributes and labels in your Chatwoot instance,
checks for redundancy, and provides a clean overview.

Usage:
    python audit_attributes.py

Requirements:
    - Set environment variables: CW_URL, CW_ACC_ID, CW_ADMIN_TOKEN
"""

import os
import requests
from datetime import datetime

# Configuration
CW_URL = os.getenv("CW_URL", "https://crm.stephenadei.nl")
ACC_ID = os.getenv("CW_ACC_ID", "1")
ADMIN_TOKEN = os.getenv("CW_ADMIN_TOKEN", "mCNRQJzK4KbVuinP7NszBTug")

def get_api_data(endpoint):
    """Fetch data from Chatwoot API"""
    url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/{endpoint}"
    headers = {"Api-Access-Token": ADMIN_TOKEN}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to fetch {endpoint}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error fetching {endpoint}: {e}")
        return None

def audit_custom_attributes():
    """Audit all custom attributes"""
    print("🔍 Auditing Custom Attributes...")
    print("=" * 50)
    
    # Get all custom attribute definitions
    attributes = get_api_data("custom_attribute_definitions")
    if not attributes:
        return
    
    # Separate by model type
    contact_attrs = [attr for attr in attributes if attr.get("attribute_model") == "contact_attribute"]
    conversation_attrs = [attr for attr in attributes if attr.get("attribute_model") == "conversation_attribute"]
    
    print(f"📊 Found {len(contact_attrs)} contact attributes and {len(conversation_attrs)} conversation attributes")
    print()
    
    # Contact Attributes
    print("👤 CONTACT ATTRIBUTES:")
    print("-" * 30)
    for attr in sorted(contact_attrs, key=lambda x: x.get("attribute_key", "")):
        key = attr.get("attribute_key", "unknown")
        name = attr.get("attribute_display_name", "Unknown")
        created_at = attr.get("created_at", "unknown")
        print(f"  • {key:20} → {name}")
    
    print()
    
    # Conversation Attributes
    print("💬 CONVERSATION ATTRIBUTES:")
    print("-" * 30)
    for attr in sorted(conversation_attrs, key=lambda x: x.get("attribute_key", "")):
        key = attr.get("attribute_key", "unknown")
        name = attr.get("attribute_display_name", "Unknown")
        created_at = attr.get("created_at", "unknown")
        print(f"  • {key:20} → {name}")
    
    print()

def audit_labels():
    """Audit all labels"""
    print("🏷️  Auditing Labels...")
    print("=" * 50)
    
    # Get all labels
    labels_data = get_api_data("labels")
    if not labels_data:
        return
    
    # Handle different response formats
    if isinstance(labels_data, list):
        labels = labels_data
    elif isinstance(labels_data, dict) and "payload" in labels_data:
        labels = labels_data["payload"]
    else:
        print(f"❌ Unexpected labels data format: {type(labels_data)}")
        return
    
    print(f"📊 Found {len(labels)} labels")
    print()
    
    # Sort labels alphabetically
    sorted_labels = sorted(labels, key=lambda x: x.get("title", ""))
    
    for label in sorted_labels:
        title = label.get("title", "unknown")
        description = label.get("description", "")
        created_at = label.get("created_at", "unknown")
        
        if description:
            print(f"  • {title:20} → {description}")
        else:
            print(f"  • {title}")
    
    print()

def check_redundancy():
    """Check for redundant or unused attributes"""
    print("🔍 Checking for Redundancy...")
    print("=" * 50)
    
    # Get all attributes
    attributes = get_api_data("custom_attribute_definitions")
    if not attributes:
        return
    
    # Check for similar names
    contact_attrs = [attr for attr in attributes if attr.get("attribute_model") == "contact_attribute"]
    
    # Group by similar names
    name_groups = {}
    for attr in contact_attrs:
        key = attr.get("attribute_key", "").lower()
        name = attr.get("attribute_display_name", "").lower()
        
        # Check for similar keys
        for existing_key in name_groups.keys():
            if key in existing_key or existing_key in key:
                if existing_key not in name_groups:
                    name_groups[existing_key] = []
                name_groups[existing_key].append(attr)
                break
        else:
            name_groups[key] = [attr]
    
    # Report potential redundancies
    redundancies_found = False
    for key, attrs in name_groups.items():
        if len(attrs) > 1:
            if not redundancies_found:
                print("⚠️  Potential redundancies found:")
                redundancies_found = True
            
            print(f"  Similar to '{key}':")
            for attr in attrs:
                print(f"    • {attr.get('attribute_key')} → {attr.get('attribute_display_name')}")
            print()
    
    if not redundancies_found:
        print("✅ No obvious redundancies found")
    
    print()

def generate_cleanup_report():
    """Generate a cleanup report with recommendations"""
    print("📋 Cleanup Report & Recommendations")
    print("=" * 50)
    
    # Get current data
    attributes = get_api_data("custom_attribute_definitions")
    labels_data = get_api_data("labels")
    
    if not attributes or not labels_data:
        print("❌ Could not fetch data for cleanup report")
        return
    
    # Handle different response formats for labels
    if isinstance(labels_data, list):
        labels = labels_data
    elif isinstance(labels_data, dict) and "payload" in labels_data:
        labels = labels_data["payload"]
    else:
        print(f"❌ Unexpected labels data format: {type(labels_data)}")
        return
    
    # Count by type
    contact_attrs = [attr for attr in attributes if attr.get("attribute_model") == "contact_attribute"]
    conversation_attrs = [attr for attr in attributes if attr.get("attribute_model") == "conversation_attribute"]
    
    print(f"📊 Current Status:")
    print(f"  • Contact attributes: {len(contact_attrs)}")
    print(f"  • Conversation attributes: {len(conversation_attrs)}")
    print(f"  • Labels: {len(labels)}")
    print()
    
    # Check for unused attributes (not in our bot's list)
    bot_contact_attrs = {
        "first_name", "language", "is_adult", "guardian_consent", "guardian_name",
        "guardian_phone", "guardian_verified_at", "is_student", "is_parent",
        "student_since", "parent_since", "education_level", "subject", "year",
        "format_preference", "welcome_done", "first_contact_at", "name_asked_at",
        "age_verified_at", "wknd_eligible"
    }
    
    bot_conversation_attrs = {"age_verified", "pending_intent"}
    
    bot_labels = {
        "new_client", "returning_client", "needs_guardian", "minor",
        "age_verified", "weekend_discount", "needs_parent_contact"
    }
    
    # Find unused attributes
    existing_contact_keys = {attr.get("attribute_key") for attr in contact_attrs}
    existing_conversation_keys = {attr.get("attribute_key") for attr in conversation_attrs}
    existing_label_titles = {label.get("title") for label in labels}
    
    unused_contact = existing_contact_keys - bot_contact_attrs
    unused_conversation = existing_conversation_keys - bot_conversation_attrs
    unused_labels = existing_label_titles - bot_labels
    
    if unused_contact:
        print("🗑️  Unused Contact Attributes (can be removed):")
        for key in sorted(unused_contact):
            print(f"  • {key}")
        print()
    
    if unused_conversation:
        print("🗑️  Unused Conversation Attributes (can be removed):")
        for key in sorted(unused_conversation):
            print(f"  • {key}")
        print()
    
    if unused_labels:
        print("🗑️  Unused Labels (can be removed):")
        for title in sorted(unused_labels):
            print(f"  • {title}")
        print()
    
    if not (unused_contact or unused_conversation or unused_labels):
        print("✅ All attributes and labels are being used by the bot")
    
    print("💡 Recommendations:")
    print("  • Keep all bot-related attributes and labels")
    print("  • Consider removing unused ones if they're not needed")
    print("  • Regular audits help maintain a clean setup")

def main():
    """Main audit function"""
    print("🔍 CHATWOOT ATTRIBUTES & LABELS AUDIT")
    print("=" * 60)
    print(f"📅 Audit Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Chatwoot URL: {CW_URL}")
    print(f"📊 Account ID: {ACC_ID}")
    print("=" * 60)
    print()
    
    # Run all audits
    audit_custom_attributes()
    audit_labels()
    check_redundancy()
    generate_cleanup_report()
    
    print("🎉 Audit completed!")

if __name__ == "__main__":
    main() 