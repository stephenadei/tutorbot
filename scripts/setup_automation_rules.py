#!/usr/bin/env python3
"""
Chatwoot Automation Rules Setup Script
======================================

This script sets up automation rules in Chatwoot to automatically
assign labels based on custom attributes for better workflow management.

Usage:
    python setup_automation_rules.py

Requirements:
    - Set environment variables: CW_URL, CW_ACC_ID, CW_ADMIN_TOKEN
"""

import os
import requests
import json
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

def create_automation_rule(rule_data):
    """Create an automation rule"""
    url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/automation_rules"
    headers = {"Api-Access-Token": ADMIN_TOKEN, "Content-Type": "application/json"}
    
    try:
        response = requests.post(url, headers=headers, json=rule_data, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to create automation rule: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating automation rule: {e}")
        return None

def setup_age_management_rules():
    """Setup automation rules for age management"""
    print("👶 Setting up age management automation rules...")
    
    # Rule 1: Minor needs guardian
    minor_rule = {
        "name": "Minor Needs Guardian",
        "description": "Automatically add 'needs_guardian' label when contact is marked as minor",
        "event_name": "contact_updated",
        "conditions": [
            {
                "attribute_key": "is_adult",
                "filter_operator": "equal_to",
                "query_operator": "AND",
                "values": ["false"]
            }
        ],
        "actions": [
            {
                "action_name": "add_label",
                "action_params": ["needs_guardian"]
            }
        ]
    }
    
    result = create_automation_rule(minor_rule)
    if result:
        print("✅ Minor needs guardian rule created")
    else:
        print("❌ Failed to create minor needs guardian rule")
    
    # Rule 2: Age verified
    age_verified_rule = {
        "name": "Age Verified",
        "description": "Add 'age_verified' label when age is verified",
        "event_name": "contact_updated",
        "conditions": [
            {
                "attribute_key": "age_verified_at",
                "filter_operator": "is_present",
                "query_operator": "AND",
                "values": []
            }
        ],
        "actions": [
            {
                "action_name": "add_label",
                "action_params": ["age_verified"]
            }
        ]
    }
    
    result = create_automation_rule(age_verified_rule)
    if result:
        print("✅ Age verified rule created")
    else:
        print("❌ Failed to create age verified rule")
    
    print()

def setup_student_management_rules():
    """Setup automation rules for student management"""
    print("🎓 Setting up student management automation rules...")
    
    # Rule 1: New student
    new_student_rule = {
        "name": "New Student Registration",
        "description": "Add 'new_client' label when someone becomes a student",
        "event_name": "contact_updated",
        "conditions": [
            {
                "attribute_key": "is_student",
                "filter_operator": "equal_to",
                "query_operator": "AND",
                "values": ["true"]
            },
            {
                "attribute_key": "welcome_done",
                "filter_operator": "equal_to",
                "query_operator": "AND",
                "values": ["false"]
            }
        ],
        "actions": [
            {
                "action_name": "add_label",
                "action_params": ["new_client"]
            }
        ]
    }
    
    result = create_automation_rule(new_student_rule)
    if result:
        print("✅ New student rule created")
    else:
        print("❌ Failed to create new student rule")
    
    # Rule 2: Returning student
    returning_student_rule = {
        "name": "Returning Student",
        "description": "Add 'returning_client' label for existing students",
        "event_name": "contact_updated",
        "conditions": [
            {
                "attribute_key": "is_student",
                "filter_operator": "equal_to",
                "query_operator": "AND",
                "values": ["true"]
            },
            {
                "attribute_key": "welcome_done",
                "filter_operator": "equal_to",
                "query_operator": "AND",
                "values": ["true"]
            }
        ],
        "actions": [
            {
                "action_name": "add_label",
                "action_params": ["returning_client"]
            }
        ]
    }
    
    result = create_automation_rule(returning_student_rule)
    if result:
        print("✅ Returning student rule created")
    else:
        print("❌ Failed to create returning student rule")
    
    print()

def setup_guardian_management_rules():
    """Setup automation rules for guardian management"""
    print("👨‍👩‍👧‍👦 Setting up guardian management automation rules...")
    
    # Rule 1: Needs parent contact
    parent_contact_rule = {
        "name": "Needs Parent Contact",
        "description": "Add 'needs_parent_contact' label when minor needs parent contact",
        "event_name": "contact_updated",
        "conditions": [
            {
                "attribute_key": "is_adult",
                "filter_operator": "equal_to",
                "query_operator": "AND",
                "values": ["false"]
            },
            {
                "attribute_key": "guardian_consent",
                "filter_operator": "equal_to",
                "query_operator": "AND",
                "values": [""]
            }
        ],
        "actions": [
            {
                "action_name": "add_label",
                "action_params": ["needs_parent_contact"]
            }
        ]
    }
    
    result = create_automation_rule(parent_contact_rule)
    if result:
        print("✅ Needs parent contact rule created")
    else:
        print("❌ Failed to create needs parent contact rule")
    
    print()

def setup_weekend_discount_rules():
    """Setup automation rules for weekend discount"""
    print("🎉 Setting up weekend discount automation rules...")
    
    # Rule 1: Weekend eligible
    weekend_rule = {
        "name": "Weekend Discount Eligible",
        "description": "Add 'weekend_discount' label when contact is eligible for weekend discount",
        "event_name": "contact_updated",
        "conditions": [
            {
                "attribute_key": "wknd_eligible",
                "filter_operator": "equal_to",
                "query_operator": "AND",
                "values": ["true"]
            }
        ],
        "actions": [
            {
                "action_name": "add_label",
                "action_params": ["weekend_discount"]
            }
        ]
    }
    
    result = create_automation_rule(weekend_rule)
    if result:
        print("✅ Weekend discount rule created")
    else:
        print("❌ Failed to create weekend discount rule")
    
    print()

def list_existing_rules():
    """List existing automation rules"""
    print("📋 Existing Automation Rules:")
    print("-" * 50)
    
    rules_data = get_api_data("automation_rules")
    if not rules_data:
        print("❌ Could not fetch automation rules")
        return
    
    # Handle different response formats
    if isinstance(rules_data, list):
        rules = rules_data
    elif isinstance(rules_data, dict) and "payload" in rules_data:
        rules = rules_data["payload"]
    else:
        print(f"❌ Unexpected rules data format: {type(rules_data)}")
        return
    
    if len(rules) == 0:
        print("📭 No automation rules found")
    else:
        for i, rule in enumerate(rules, 1):
            name = rule.get("name", "Unknown")
            description = rule.get("description", "No description")
            event = rule.get("event_name", "Unknown")
            print(f"{i}. {name}")
            print(f"   Event: {event}")
            print(f"   Description: {description}")
            print()
    
    print()

def main():
    """Main function to setup automation rules"""
    print("🤖 CHATWOOT AUTOMATION RULES SETUP")
    print("=" * 60)
    print(f"📅 Setup Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Chatwoot URL: {CW_URL}")
    print(f"📊 Account ID: {ACC_ID}")
    print("=" * 60)
    print()
    
    # Check connection
    print("🔍 Testing API connection...")
    test_response = requests.get(f"{CW_URL}/api/v1/accounts/{ACC_ID}/agents",
        headers={"Api-Access-Token": ADMIN_TOKEN}, timeout=10)
    
    if test_response.status_code != 200:
        print("❌ Cannot connect to Chatwoot API")
        print(f"   Status: {test_response.status_code}")
        return
    
    print("✅ API connection successful!")
    print()
    
    # List existing rules
    list_existing_rules()
    
    # Setup automation rules
    setup_age_management_rules()
    setup_student_management_rules()
    setup_guardian_management_rules()
    setup_weekend_discount_rules()
    
    print("🎉 Automation rules setup completed!")
    print()
    print("💡 Next steps:")
    print("   1. Test the automation rules with new contacts")
    print("   2. Monitor the rules in Chatwoot dashboard")
    print("   3. Adjust rules if needed")

if __name__ == "__main__":
    main() 