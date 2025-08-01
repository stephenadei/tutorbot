#!/usr/bin/env python3
"""
List all Chatwoot automation rules and compare with bot implementation
"""
import os
import requests
import json

CW_URL = os.environ.get("CW_URL", "https://crm.stephenadei.nl")
ACC = os.environ.get("CW_ACCOUNT_ID", "1")
ADMIN_TOKEN = os.environ.get("CW_ADMIN_TOKEN")

if not ADMIN_TOKEN:
    print("❌ CW_ADMIN_TOKEN not set in environment!")
    exit(1)

headers = {
    "api_access_token": ADMIN_TOKEN,
    "Content-Type": "application/json"
}

def get_automation_rules():
    """Get all automation rules"""
    url = f"{CW_URL}/api/v1/accounts/{ACC}/automation_rules"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get automation rules: {response.status_code} {response.text}")
            return []
    except Exception as e:
        print(f"❌ Exception getting automation rules: {e}")
        return []

def get_contact_attributes():
    """Get all contact custom attributes"""
    url = f"{CW_URL}/api/v1/accounts/{ACC}/custom_attribute_definitions"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return [attr for attr in data if attr.get("attribute_model") == "contact_attribute"]
        else:
            print(f"❌ Failed to get custom attributes: {response.status_code} {response.text}")
            return []
    except Exception as e:
        print(f"❌ Exception getting custom attributes: {e}")
        return []

def get_conversation_attributes():
    """Get all conversation custom attributes"""
    url = f"{CW_URL}/api/v1/accounts/{ACC}/custom_attribute_definitions"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return [attr for attr in data if attr.get("attribute_model") == "conversation_attribute"]
        else:
            print(f"❌ Failed to get custom attributes: {response.status_code} {response.text}")
            return []
    except Exception as e:
        print(f"❌ Exception getting custom attributes: {e}")
        return []

def get_labels():
    """Get all labels"""
    url = f"{CW_URL}/api/v1/accounts/{ACC}/labels"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get labels: {response.status_code} {response.text}")
            return []
    except Exception as e:
        print(f"❌ Exception getting labels: {e}")
        return []

def analyze_bot_implementation():
    """Analyze our bot implementation"""
    print("\n🤖 BOT IMPLEMENTATION ANALYSIS")
    print("=" * 50)
    
    # Read main.py to analyze implementation
    try:
        with open("main.py", "r") as f:
            content = f.read()
        
        # Analyze custom attributes used
        print("\n📋 Custom Attributes Used in Bot:")
        contact_attrs = [
            "language", "segment", "first_name", "name", "is_adult", 
            "format_preference", "relationship_to_learner", "learner_name"
        ]
        conv_attrs = [
            "pending_intent", "intake_step", "planning_profile", 
            "last_bot_message", "language_just_set", "language_prompted",
            "intake_completed", "learner_name", "relationship_to_learner"
        ]
        
        print("Contact attributes:")
        for attr in contact_attrs:
            if attr in content:
                print(f"  ✅ {attr}")
            else:
                print(f"  ❌ {attr} (not found)")
        
        print("\nConversation attributes:")
        for attr in conv_attrs:
            if attr in content:
                print(f"  ✅ {attr}")
            else:
                print(f"  ❌ {attr} (not found)")
        
        # Analyze labels used
        print("\n🏷️ Labels Used in Bot:")
        labels = [
            "intent:handoff:duplicate", "intent:handoff:auto", 
            "intent:handoff:teacher", "status:awaiting_pay", 
            "payment:paid", "status:booked", "intent_handoff_teacher"
        ]
        
        for label in labels:
            if label in content:
                print(f"  ✅ {label}")
            else:
                print(f"  ❌ {label} (not found)")
        
        # Analyze intents/flows
        print("\n🎯 Intents/Flows in Bot:")
        intents = [
            "intake", "planning", "handoff", "info_menu"
        ]
        
        for intent in intents:
            if intent in content:
                print(f"  ✅ {intent}")
            else:
                print(f"  ❌ {intent} (not found)")
        
    except Exception as e:
        print(f"❌ Error reading main.py: {e}")

def main():
    print(f"🔍 Analyzing Chatwoot automation for {CW_URL} (account {ACC})...")
    print()
    
    # Get automation rules
    print("📋 AUTOMATION RULES")
    print("=" * 50)
    automation_rules = get_automation_rules()
    
    if automation_rules:
        print(f"Found {len(automation_rules)} automation rules")
        for i, rule in enumerate(automation_rules, 1):
            if isinstance(rule, dict):
                print(f"\n{i}. {rule.get('name', 'Unnamed Rule')}")
                print(f"   ID: {rule.get('id')}")
                print(f"   Active: {rule.get('active', False)}")
                print(f"   Event: {rule.get('event_name', 'Unknown')}")
                print(f"   Conditions: {len(rule.get('conditions', []))}")
                print(f"   Actions: {len(rule.get('actions', []))}")
                
                # Show conditions
                conditions = rule.get('conditions', [])
                if conditions:
                    print("   Conditions:")
                    for cond in conditions:
                        print(f"     - {cond.get('attribute_key', 'Unknown')} {cond.get('filter_operator', 'Unknown')} {cond.get('values', [])}")
                
                # Show actions
                actions = rule.get('actions', [])
                if actions:
                    print("   Actions:")
                    for action in actions:
                        action_type = action.get('action_name', 'Unknown')
                        if action_type == 'add_label':
                            print(f"     - Add label: {action.get('action_params', {}).get('labels', [])}")
                        elif action_type == 'assign_team':
                            print(f"     - Assign team: {action.get('action_params', {}).get('team_ids', [])}")
                        elif action_type == 'assign_agent':
                            print(f"     - Assign agent: {action.get('action_params', {}).get('assignee_id', 'Unknown')}")
                        elif action_type == 'send_message':
                            print(f"     - Send message: {action.get('action_params', {}).get('message', 'Unknown')[:50]}...")
                        else:
                            print(f"     - {action_type}: {action.get('action_params', {})}")
            else:
                print(f"\n{i}. {rule} (not a dict)")
    else:
        print("❌ No automation rules found")
    
    # Get custom attributes
    print("\n📝 CUSTOM ATTRIBUTES")
    print("=" * 50)
    
    contact_attrs = get_contact_attributes()
    print(f"\nContact Attributes ({len(contact_attrs)}):")
    for attr in contact_attrs:
        print(f"  • {attr.get('attribute_key')} ({attr.get('attribute_type')}) - {attr.get('attribute_display_name')}")
        if attr.get('attribute_values'):
            print(f"    Values: {attr.get('attribute_values')}")
    
    conv_attrs = get_conversation_attributes()
    print(f"\nConversation Attributes ({len(conv_attrs)}):")
    for attr in conv_attrs:
        print(f"  • {attr.get('attribute_key')} ({attr.get('attribute_type')}) - {attr.get('attribute_display_name')}")
        if attr.get('attribute_values'):
            print(f"    Values: {attr.get('attribute_values')}")
    
    # Get labels
    print("\n🏷️ LABELS")
    print("=" * 50)
    labels = get_labels()
    if labels:
        for label in labels:
            if isinstance(label, dict):
                print(f"  • {label.get('title')} ({label.get('color', 'No color')})")
            else:
                print(f"  • {label} (not a dict)")
    else:
        print("❌ No labels found")
    
    # Analyze bot implementation
    analyze_bot_implementation()
    
    print("\n" + "=" * 50)
    print("✅ Analysis complete!")

if __name__ == "__main__":
    main() 