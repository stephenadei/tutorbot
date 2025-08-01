#!/usr/bin/env python3
"""
Chatwoot Setup Script voor TutorBot
Configureert automatisch alle benodigde custom attributes, labels en automation rules.
"""

import os
import requests
import json
from typing import Dict, List, Any

# Configuratie
CW_URL = os.getenv("CW_URL", "https://crm.stephenadei.nl")
ACC = os.getenv("CW_ACC_ID", "1")
ADMIN_TOK = os.getenv("CW_ADMIN_TOKEN")

if not ADMIN_TOK:
    print("❌ CW_ADMIN_TOKEN niet geconfigureerd")
    exit(1)

headers = {
    "api_access_token": ADMIN_TOK,
    "Content-Type": "application/json"
}

def make_request(method: str, endpoint: str, data: Dict = None) -> Dict:
    """Maak HTTP request naar Chatwoot API"""
    url = f"{CW_URL}/api/v1/accounts/{ACC}/{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"❌ {method} {endpoint}: {response.status_code} - {response.text}")
            return {}
            
    except Exception as e:
        print(f"❌ Error bij {method} {endpoint}: {e}")
        return {}

def setup_contact_attributes():
    """Setup contact custom attributes"""
    print("🔧 Setting up contact attributes...")
    
    contact_attributes = {
        "language": {
            "attribute_display_type": "list",
            "attribute_display_name": "Language",
            "attribute_description": "Preferred communication language",
            "attribute_key": "language",
            "attribute_values": ["nl", "en"]
        },
        "school_level": {
            "attribute_display_type": "list",
            "attribute_display_name": "School Level",
            "attribute_description": "Current education level",
            "attribute_key": "school_level",
            "attribute_values": ["po", "vmbo", "havo", "vwo", "mbo", "university_wo", "university_hbo", "adult"]
        },
        "customer_since": {
            "attribute_display_type": "date",
            "attribute_display_name": "Customer Since",
            "attribute_description": "Date when customer first contacted",
            "attribute_key": "customer_since"
        },
        "postcode": {
            "attribute_display_type": "text",
            "attribute_display_name": "Postcode",
            "attribute_description": "Customer postcode",
            "attribute_key": "postcode"
        },
        "distance_km": {
            "attribute_display_type": "number",
            "attribute_display_name": "Distance (km)",
            "attribute_description": "Distance from tutor location",
            "attribute_key": "distance_km"
        },
        "segment": {
            "attribute_display_type": "list",
            "attribute_display_name": "Segment",
            "attribute_description": "Customer segment for pricing and flow",
            "attribute_key": "segment",
            "attribute_values": ["new", "existing", "returning_broadcast", "weekend"]
        },
        "weekend_whitelisted": {
            "attribute_display_type": "checkbox",
            "attribute_display_name": "Weekend Whitelisted",
            "attribute_description": "Access to weekend pricing",
            "attribute_key": "weekend_whitelisted"
        }
    }
    
    for key, attr in contact_attributes.items():
        print(f"  📝 Creating contact attribute: {key}")
        result = make_request("POST", "custom_attribute_definitions", attr)
        if result:
            print(f"  ✅ Created: {key}")
        else:
            print(f"  ⚠️  May already exist: {key}")

def setup_conversation_attributes():
    """Setup conversation custom attributes"""
    print("🔧 Setting up conversation attributes...")
    
    conversation_attributes = {
        "program": {
            "attribute_display_type": "list",
            "attribute_display_name": "Program",
            "attribute_description": "Specific program or curriculum",
            "attribute_key": "program",
            "attribute_values": ["none", "mbo_rekenen_2f", "mbo_rekenen_3f", "ib_math_sl", "ib_math_hl", "cambridge"]
        },
        "topic_primary": {
            "attribute_display_type": "text",
            "attribute_display_name": "Primary Topic",
            "attribute_description": "Main subject or topic",
            "attribute_key": "topic_primary"
        },
        "topic_secondary": {
            "attribute_display_type": "text",
            "attribute_display_name": "Secondary Topic",
            "attribute_description": "Additional topics or goals",
            "attribute_key": "topic_secondary"
        },
        "toolset": {
            "attribute_display_type": "text",
            "attribute_display_name": "Toolset",
            "attribute_description": "Tools or software used",
            "attribute_key": "toolset"
        },
        "lesson_mode": {
            "attribute_display_type": "list",
            "attribute_display_name": "Lesson Mode",
            "attribute_description": "Preferred lesson format",
            "attribute_key": "lesson_mode",
            "attribute_values": ["online", "in_person", "hybrid"]
        },
        "is_adult": {
            "attribute_display_type": "checkbox",
            "attribute_display_name": "Is Adult",
            "attribute_description": "Student is 18+ years old",
            "attribute_key": "is_adult"
        },
        "relationship_to_learner": {
            "attribute_display_type": "text",
            "attribute_display_name": "Relationship to Learner",
            "attribute_description": "Relationship if booking for someone else",
            "attribute_key": "relationship_to_learner"
        },
        "language_prompted": {
            "attribute_display_type": "checkbox",
            "attribute_display_name": "Language Prompted",
            "attribute_description": "Language selection has been prompted",
            "attribute_key": "language_prompted"
        },
        "intake_completed": {
            "attribute_display_type": "checkbox",
            "attribute_display_name": "Intake Completed",
            "attribute_description": "Student intake process completed",
            "attribute_key": "intake_completed"
        },
        "planning_profile": {
            "attribute_display_type": "list",
            "attribute_display_name": "Planning Profile",
            "attribute_description": "Planning profile for slot suggestions",
            "attribute_key": "planning_profile",
            "attribute_values": ["new", "existing", "returning_broadcast", "weekend"]
        },
        "order_id": {
            "attribute_display_type": "text",
            "attribute_display_name": "Order ID",
            "attribute_description": "Payment order identifier",
            "attribute_key": "order_id"
        }
    }
    
    for key, attr in conversation_attributes.items():
        print(f"  📝 Creating conversation attribute: {key}")
        result = make_request("POST", "custom_attribute_definitions", attr)
        if result:
            print(f"  ✅ Created: {key}")
        else:
            print(f"  ⚠️  May already exist: {key}")

def setup_labels():
    """Setup conversation labels"""
    print("🔧 Setting up labels...")
    
    labels = [
        # Audience (exact 1)
        "audience:po", "audience:vmbo", "audience:havo", "audience:vwo", "audience:mbo",
        "audience:university:wo", "audience:university:hbo", "audience:adult",
        
        # Subject
        "subject:math", "subject:stats", "subject:science", "subject:english",
        "subject:data-science", "subject:programming", "subject:didactics",
        "subject:economics", "subject:creative",
        
        # Service
        "service:trial", "service:1on1", "service:group", "service:exam-prep",
        "service:workshop", "service:project-supervision", "service:consultancy",
        
        # Process
        "status:awaiting_reply", "status:booked", "status:awaiting_pay",
        "payment:paid", "payment:overdue", "priority:urgent", "flag:vip",
        "flag:spam", "price:custom",
        
        # Intent
        "intent:handoff:teacher", "intent:info"
    ]
    
    for label in labels:
        print(f"  📝 Creating label: {label}")
        data = {"title": label}
        result = make_request("POST", "labels", data)
        if result:
            print(f"  ✅ Created: {label}")
        else:
            print(f"  ⚠️  May already exist: {label}")

def setup_teams():
    """Setup teams for routing"""
    print("🔧 Setting up teams...")
    
    teams = [
        {
            "name": "Data/Programming",
            "description": "Programming and data science subjects"
        },
        {
            "name": "VO-docenten",
            "description": "Secondary education teachers"
        },
        {
            "name": "HO/Universiteit",
            "description": "Higher education and university"
        }
    ]
    
    for team in teams:
        print(f"  📝 Creating team: {team['name']}")
        result = make_request("POST", "teams", team)
        if result:
            print(f"  ✅ Created: {team['name']}")
        else:
            print(f"  ⚠️  May already exist: {team['name']}")

def list_existing():
    """List existing configuration"""
    print("📋 Existing configuration:")
    
    # List contact attributes
    print("\n🔧 Contact Attributes:")
    result = make_request("GET", "custom_attribute_definitions")
    if result:
        for attr in result.get("payload", []):
            if attr.get("attribute_model") == "ContactAttribute":
                print(f"  ✅ {attr.get('attribute_key')}: {attr.get('attribute_display_name')}")
    
    # List conversation attributes
    print("\n🔧 Conversation Attributes:")
    if result:
        for attr in result.get("payload", []):
            if attr.get("attribute_model") == "ConversationAttribute":
                print(f"  ✅ {attr.get('attribute_key')}: {attr.get('attribute_display_name')}")
    
    # List labels
    print("\n🏷️ Labels:")
    result = make_request("GET", "labels")
    if result:
        for label in result.get("payload", []):
            print(f"  ✅ {label.get('title')}")
    
    # List teams
    print("\n👥 Teams:")
    result = make_request("GET", "teams")
    if result:
        for team in result.get("payload", []):
            print(f"  ✅ {team.get('name')}: {team.get('description')}")

def main():
    """Main setup function"""
    print("🚀 TutorBot Chatwoot Setup")
    print("=" * 50)
    
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "list":
        list_existing()
        return
    
    print("📝 This script will configure Chatwoot with all required:")
    print("  • Contact custom attributes")
    print("  • Conversation custom attributes") 
    print("  • Labels")
    print("  • Teams")
    print()
    
    response = input("Continue? (y/N): ")
    if response.lower() != 'y':
        print("❌ Setup cancelled")
        return
    
    setup_contact_attributes()
    setup_conversation_attributes()
    setup_labels()
    setup_teams()
    
    print("\n✅ Setup complete!")
    print("\n📋 Next steps:")
    print("1. Configure webhook URL in Chatwoot: https://your-domain.com/cw")
    print("2. Set HMAC secret in environment variables")
    print("3. Test with a new conversation")
    print("4. Check logs for any errors")

if __name__ == "__main__":
    main() 