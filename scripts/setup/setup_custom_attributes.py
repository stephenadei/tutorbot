#!/usr/bin/env python3
"""
Setup custom attribute definitions for the tutoring bot
"""
import os
import requests

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

# Define all the custom attributes we need
contact_attributes = [
    {
        "attribute_display_name": "Language",
        "attribute_key": "language",
        "attribute_description": "Preferred language for communication",
        "attribute_model": "contact_attribute",
        "attribute_type": "list",
        "attribute_values": ["nl", "en"],
        "default_value": ""
    },
    {
        "attribute_display_name": "Segment",
        "attribute_key": "segment",
        "attribute_description": "Customer segment for routing",
        "attribute_model": "contact_attribute",
        "attribute_type": "list",
        "attribute_values": ["new", "existing", "returning_broadcast", "weekend"],
        "default_value": ""
    },
    {
        "attribute_display_name": "School Level",
        "attribute_key": "school_level",
        "attribute_description": "Education level of the learner",
        "attribute_model": "contact_attribute",
        "attribute_type": "list",
        "attribute_values": ["po", "vmbo", "havo", "vwo", "mbo", "university_wo", "university_hbo", "adult"],
        "default_value": ""
    },
    {
        "attribute_display_name": "Subject",
        "attribute_key": "subject",
        "attribute_description": "Main subject for tutoring",
        "attribute_model": "contact_attribute",
        "attribute_type": "list",
        "attribute_values": ["math", "dutch", "english", "physics", "chemistry", "biology", "history", "geography"],
        "default_value": ""
    }
]

conversation_attributes = [
    {
        "attribute_display_name": "Program",
        "attribute_key": "program",
        "attribute_description": "Specific tutoring program",
        "attribute_model": "conversation_attribute",
        "attribute_type": "text",
        "default_value": ""
    },
    {
        "attribute_display_name": "Lesson Mode",
        "attribute_key": "lesson_mode",
        "attribute_description": "How the lesson will be conducted",
        "attribute_model": "conversation_attribute",
        "attribute_type": "list",
        "attribute_values": ["online", "in_person", "hybrid"],
        "default_value": ""
    },
    {
        "attribute_display_name": "Trial Status",
        "attribute_key": "trial_status",
        "attribute_description": "Status of trial lesson",
        "attribute_model": "conversation_attribute",
        "attribute_type": "list",
        "attribute_values": ["requested", "scheduled", "completed", "converted"],
        "default_value": ""
    },
    {
        "attribute_display_name": "Payment Status",
        "attribute_key": "payment_status",
        "attribute_description": "Payment status for services",
        "attribute_model": "conversation_attribute",
        "attribute_type": "list",
        "attribute_values": ["pending", "paid", "failed", "refunded"],
        "default_value": ""
    }
]

def create_attribute_definition(attr_def):
    """Create a custom attribute definition"""
    url = f"{CW_URL}/api/v1/accounts/{ACC}/custom_attribute_definitions"
    
    try:
        response = requests.post(url, headers=headers, json=attr_def)
        if response.status_code == 200:
            print(f"✅ Created {attr_def['attribute_model']}: {attr_def['attribute_key']}")
            return True
        elif response.status_code == 422:
            print(f"⚠️  Already exists {attr_def['attribute_model']}: {attr_def['attribute_key']}")
            return True
        else:
            print(f"❌ Failed to create {attr_def['attribute_key']}: {response.status_code} {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception creating {attr_def['attribute_key']}: {e}")
        return False

def main():
    print(f"Setting up custom attributes for {CW_URL} (account {ACC})...")
    print()
    
    # Create contact attributes
    print("📝 Creating contact attributes...")
    for attr in contact_attributes:
        create_attribute_definition(attr)
    
    print()
    
    # Create conversation attributes
    print("📝 Creating conversation attributes...")
    for attr in conversation_attributes:
        create_attribute_definition(attr)
    
    print()
    print("✅ Custom attribute setup complete!")

if __name__ == "__main__":
    main() 