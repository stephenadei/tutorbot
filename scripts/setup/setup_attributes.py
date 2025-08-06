#!/usr/bin/env python3
"""
Chatwoot Custom Attributes Setup Script
Automatically creates all custom attributes from YAML config files via Chatwoot API
"""

import os
import sys
import yaml
import requests
import time
from typing import List, Dict, Any

def ensure_project_root():
    """Ensure we're running from the project root directory"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Project root should be one level up from scripts
    project_root = os.path.dirname(script_dir)
    
    # Check if we're in the right place by looking for key files
    required_files = [
        "main.py",
        "requirements.txt", 
        "config/contact_attributes.yaml",
        "config/conversation_attributes.yaml"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(project_root, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Error: Script must be run from the project root directory!")
        print(f"   Current directory: {os.getcwd()}")
        print(f"   Expected project root: {project_root}")
        print(f"   Missing files: {', '.join(missing_files)}")
        print(f"\n💡 Solution: Run from the project root:")
        print(f"   cd {project_root}")
        print(f"   python3 scripts/setup_attributes.py")
        sys.exit(1)
    
    # Change to project root if we're not already there
    if os.getcwd() != project_root:
        print(f"🔄 Changing to project root: {project_root}")
        os.chdir(project_root)
    
    return project_root

# Ensure we're in the right directory before importing anything else
PROJECT_ROOT = ensure_project_root()

# Configuration
CW_URL = os.getenv("CW_URL", "https://crm.stephenadei.nl")
ACC_ID = os.getenv("CW_ACC_ID")
ADMIN_TOKEN = os.getenv("CW_ADMIN_TOKEN")  # Admin token for setup operations

def load_attributes_config(filename: str) -> Dict[str, Dict[str, Any]]:
    """Load attributes configuration from YAML file"""
    config_path = os.path.join(PROJECT_ROOT, "config", filename)
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config.get('contact_attributes', {}) if 'contact_attributes' in config else config.get('conversation_attributes', {})
    except FileNotFoundError:
        print(f"❌ {config_path} not found!")
        return {}
    except yaml.YAMLError as e:
        print(f"❌ Error parsing {config_path}: {e}")
        return {}

def create_custom_attribute(attribute_key: str, config: Dict[str, Any], model_type: str) -> bool:
    """Create a single custom attribute via Chatwoot API"""
    url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/custom_attribute_definitions"
    headers = {
        "Api-Access-Token": ADMIN_TOKEN,
        "Content-Type": "application/json"
    }
    
    data = {
        "attribute_display_name": config.get("attribute_display_name", attribute_key),
        "attribute_display_type": config.get("attribute_display_type", "text"),
        "attribute_key": attribute_key,
        "attribute_model": model_type
    }
    
    try:
        print(f"🔧 Creating {model_type} attribute: {attribute_key}")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Created {model_type} attribute: {attribute_key}")
            return True
        elif response.status_code == 422:
            print(f"⚠️ {model_type} attribute already exists: {attribute_key}")
            return True
        else:
            print(f"❌ Failed to create {model_type} attribute {attribute_key}: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating {model_type} attribute {attribute_key}: {e}")
        return False

def setup_contact_attributes() -> None:
    """Setup all contact custom attributes"""
    print("\n📋 Setting up Contact Attributes...")
    
    contact_attrs = load_attributes_config('contact_attributes.yaml')
    if not contact_attrs:
        print("❌ No contact attributes configuration found!")
        return
    
    success_count = 0
    failed_count = 0
    
    for attr_key, config in contact_attrs.items():
        if create_custom_attribute(attr_key, config, "contact_attribute"):
            success_count += 1
        else:
            failed_count += 1
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    print(f"\n📊 Contact Attributes Summary:")
    print(f"   ✅ Successfully created: {success_count}")
    print(f"   ❌ Failed: {failed_count}")
    print(f"   📊 Total processed: {len(contact_attrs)}")

def setup_conversation_attributes() -> None:
    """Setup all conversation custom attributes"""
    print("\n📋 Setting up Conversation Attributes...")
    
    conv_attrs = load_attributes_config('conversation_attributes.yaml')
    if not conv_attrs:
        print("❌ No conversation attributes configuration found!")
        return
    
    success_count = 0
    failed_count = 0
    
    for attr_key, config in conv_attrs.items():
        if create_custom_attribute(attr_key, config, "conversation_attribute"):
            success_count += 1
        else:
            failed_count += 1
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    print(f"\n📊 Conversation Attributes Summary:")
    print(f"   ✅ Successfully created: {success_count}")
    print(f"   ❌ Failed: {failed_count}")
    print(f"   📊 Total processed: {len(conv_attrs)}")

def list_existing_attributes() -> None:
    """List all existing custom attributes in Chatwoot"""
    print("📋 Listing existing custom attributes...")
    
    # List contact attributes
    url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/custom_attribute_definitions"
    headers = {"Api-Access-Token": ADMIN_TOKEN}
    params = {"attribute_model": "contact_attribute"}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            contact_attrs = response.json()
            print(f"\n📊 Found {len(contact_attrs)} contact attributes:")
            for attr in contact_attrs:
                print(f"   • {attr.get('attribute_key')} ({attr.get('attribute_display_name')})")
        else:
            print(f"❌ Failed to fetch contact attributes: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error fetching contact attributes: {e}")
    
    # List conversation attributes
    params = {"attribute_model": "conversation_attribute"}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            conv_attrs = response.json()
            print(f"\n📊 Found {len(conv_attrs)} conversation attributes:")
            for attr in conv_attrs:
                print(f"   • {attr.get('attribute_key')} ({attr.get('attribute_display_name')})")
        else:
            print(f"❌ Failed to fetch conversation attributes: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error fetching conversation attributes: {e}")

def main():
    """Main function"""
    print("🚀 Starting Chatwoot Custom Attributes Setup...")
    print(f"   Project root: {PROJECT_ROOT}")
    print(f"   CW_URL: {CW_URL}")
    print(f"   ACC_ID: {ACC_ID}")
    print(f"   ADMIN_TOKEN: {ADMIN_TOKEN[:10]}..." if ADMIN_TOKEN else "   ADMIN_TOKEN: None")
    
    if not all([CW_URL, ACC_ID, ADMIN_TOKEN]):
        print("❌ Missing required environment variables!")
        print("   Please set: CW_URL, CW_ACC_ID, CW_ADMIN_TOKEN")
        return
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            list_existing_attributes()
        elif sys.argv[1] == "contact":
            setup_contact_attributes()
        elif sys.argv[1] == "conversation":
            setup_conversation_attributes()
        else:
            print("Usage: python3 scripts/setup_attributes.py [list|contact|conversation]")
    else:
        # Setup both
        setup_contact_attributes()
        setup_conversation_attributes()
        print("\n🎉 Custom attributes setup completed!")

if __name__ == "__main__":
    main() 