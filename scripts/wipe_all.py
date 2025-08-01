#!/usr/bin/env python3
"""
Wipe All Chatwoot Data Script
Removes all labels and custom attributes for a clean setup
"""

import os
import sys
import requests
import time
from typing import List, Dict, Any

def ensure_project_root():
    """Ensure we're running from the project root directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    required_files = [
        "main.py",
        "requirements.txt", 
        "config/contact_attributes.yaml"
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
        print(f"   python3 scripts/wipe_all.py")
        sys.exit(1)
    
    if os.getcwd() != project_root:
        print(f"🔄 Changing to project root: {project_root}")
        os.chdir(project_root)
    
    return project_root

# Ensure we're in the right directory before importing anything else
PROJECT_ROOT = ensure_project_root()

# Configuration
CW_URL = os.getenv("CW_URL", "https://crm.stephenadei.nl")
ACC_ID = os.getenv("CW_ACC_ID")
ADMIN_TOKEN = os.getenv("CW_ADMIN_TOKEN")

def get_all_labels() -> List[Dict[str, Any]]:
    """Get all labels from Chatwoot"""
    url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/labels"
    headers = {"Api-Access-Token": ADMIN_TOKEN}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "payload" in data:
                return data["payload"]
            elif isinstance(data, list):
                return data
            else:
                return []
        else:
            print(f"❌ Failed to fetch labels: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error fetching labels: {e}")
        return []

def get_all_attributes() -> Dict[str, List[Dict[str, Any]]]:
    """Get all custom attributes from Chatwoot"""
    url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/custom_attribute_definitions"
    headers = {"Api-Access-Token": ADMIN_TOKEN}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "payload" in data:
                return data["payload"]
            elif isinstance(data, list):
                return data
            else:
                return []
        else:
            print(f"❌ Failed to fetch attributes: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error fetching attributes: {e}")
        return []

def delete_label(label_id: int, label_name: str) -> bool:
    """Delete a specific label"""
    url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/labels/{label_id}"
    headers = {"Api-Access-Token": ADMIN_TOKEN}
    
    try:
        response = requests.delete(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Deleted label: {label_name}")
            return True
        else:
            print(f"❌ Failed to delete label {label_name}: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error deleting label {label_name}: {e}")
        return False

def delete_attribute(attr_id: int, attr_name: str) -> bool:
    """Delete a specific custom attribute"""
    url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/custom_attribute_definitions/{attr_id}"
    headers = {"Api-Access-Token": ADMIN_TOKEN}
    
    try:
        response = requests.delete(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Deleted attribute: {attr_name}")
            return True
        else:
            print(f"❌ Failed to delete attribute {attr_name}: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error deleting attribute {attr_name}: {e}")
        return False

def confirm_deletion(labels_count: int, attributes_count: int) -> bool:
    """Ask for confirmation before deletion"""
    print(f"\n⚠️  WARNING: This will delete ALL labels and custom attributes!")
    print(f"   📊 Labels to delete: {labels_count}")
    print(f"   📊 Attributes to delete: {attributes_count}")
    print(f"   🗑️  This action cannot be undone!")
    print(f"\n💡 Type 'WIPE ALL' to confirm deletion:")
    
    confirmation = input("> ").strip().upper()
    return confirmation == "WIPE ALL"

def wipe_all_data(auto_wipe: bool = False) -> None:
    """Main function to wipe all labels and attributes"""
    print("🗑️  Chatwoot Data Wipe Tool")
    print("=" * 50)
    
    # Get current data
    print("📋 Fetching current labels and attributes...")
    labels = get_all_labels()
    attributes = get_all_attributes()
    
    print(f"📊 Found {len(labels)} labels and {len(attributes)} custom attributes")
    
    if not labels and not attributes:
        print("✅ No data to delete!")
        return
    
    # Show what will be deleted
    if labels:
        print(f"\n📋 Labels to delete:")
        for label in labels:
            print(f"   • {label.get('title', 'Unknown')} (ID: {label.get('id', 'Unknown')})")
    
    if attributes:
        print(f"\n📋 Attributes to delete:")
        for attr in attributes:
            print(f"   • {attr.get('attribute_display_name', 'Unknown')} (ID: {attr.get('id', 'Unknown')})")
    
    # Get confirmation
    if not auto_wipe:
        if not confirm_deletion(len(labels), len(attributes)):
            print("❌ Deletion cancelled!")
            return
    else:
        print("🚀 Auto-wipe mode - skipping confirmation...")
    
    # Delete labels
    print(f"\n🗑️  Deleting {len(labels)} labels...")
    deleted_labels = 0
    failed_labels = 0
    
    for label in labels:
        label_id = label.get('id')
        label_name = label.get('title', 'Unknown')
        
        if label_id:
            if delete_label(label_id, label_name):
                deleted_labels += 1
            else:
                failed_labels += 1
        
        # Small delay to avoid rate limiting
        time.sleep(0.2)
    
    # Delete attributes
    print(f"\n🗑️  Deleting {len(attributes)} custom attributes...")
    deleted_attributes = 0
    failed_attributes = 0
    
    for attr in attributes:
        attr_id = attr.get('id')
        attr_name = attr.get('attribute_display_name', 'Unknown')
        
        if attr_id:
            if delete_attribute(attr_id, attr_name):
                deleted_attributes += 1
            else:
                failed_attributes += 1
        
        # Small delay to avoid rate limiting
        time.sleep(0.2)
    
    # Summary
    print(f"\n📊 Wipe Summary:")
    print(f"   ✅ Deleted labels: {deleted_labels}")
    print(f"   ❌ Failed labels: {failed_labels}")
    print(f"   ✅ Deleted attributes: {deleted_attributes}")
    print(f"   ❌ Failed attributes: {failed_attributes}")
    
    if deleted_labels > 0 or deleted_attributes > 0:
        print(f"\n🎉 Data wipe completed!")
        print(f"💡 You can now run setup scripts for a clean installation:")
        print(f"   python3 scripts/setup_all.py")
    else:
        print(f"\n⚠️  No data was deleted!")

def main():
    """Main function"""
    print("🚀 Starting Chatwoot Data Wipe...")
    print(f"   Project root: {PROJECT_ROOT}")
    print(f"   CW_URL: {CW_URL}")
    print(f"   ACC_ID: {ACC_ID}")
    print(f"   ADMIN_TOKEN: {ADMIN_TOKEN[:10]}..." if ADMIN_TOKEN else "   ADMIN_TOKEN: None")
    
    if not all([CW_URL, ACC_ID, ADMIN_TOKEN]):
        print("❌ Missing required environment variables!")
        print("   Please set: CW_URL, CW_ACC_ID, CW_ADMIN_TOKEN")
        return
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--auto-wipe":
            wipe_all_data(auto_wipe=True)
        elif sys.argv[1] == "--help":
            print("\n📖 Usage:")
            print("   python3 scripts/wipe_all.py              # Interactive mode")
            print("   python3 scripts/wipe_all.py --auto-wipe   # Automatic mode")
            print("   python3 scripts/wipe_all.py --help        # Show this help")
        else:
            print(f"❌ Unknown option: {sys.argv[1]}")
            print("Usage: python3 scripts/wipe_all.py [--auto-wipe|--help]")
            sys.exit(1)
    else:
        wipe_all_data(auto_wipe=False)

if __name__ == "__main__":
    main() 