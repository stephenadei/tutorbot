#!/usr/bin/env python3
"""
Chatwoot Labels Setup Script
Automatically creates all labels from YAML config file via Chatwoot API
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
        "config/labels_lean.yaml"
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
        print(f"   python3 scripts/setup_labels.py")
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

def load_labels_config() -> Dict[str, List[str]]:
    """Load labels configuration from YAML file"""
    config_path = os.path.join(PROJECT_ROOT, "config", "labels_lean.yaml")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config.get('labels', {})
    except FileNotFoundError:
        print(f"❌ {config_path} not found!")
        return {}
    except yaml.YAMLError as e:
        print(f"❌ Error parsing {config_path}: {e}")
        return {}

def create_label(label_name: str) -> bool:
    """Create a single label via Chatwoot API"""
    url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/labels"
    headers = {
        "Api-Access-Token": ADMIN_TOKEN,
        "Content-Type": "application/json"
    }
    
    data = {
        "title": label_name
    }
    
    try:
        print(f"🔧 Creating label: {label_name}")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Created label: {label_name}")
            return "created"
        elif response.status_code == 422:
            # Check if it's really a duplicate or another validation error
            error_text = response.text.lower()
            if "already exists" in error_text or "duplicate" in error_text:
                print(f"⚠️ Label already exists: {label_name}")
                return "exists"
            else:
                print(f"❌ Validation error for label {label_name}: {response.text}")
                return "failed"
        else:
            print(f"❌ Failed to create label {label_name}: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return "failed"
            
    except Exception as e:
        print(f"❌ Error creating label {label_name}: {e}")
        return "failed"

def setup_labels() -> None:
    """Setup all labels from configuration"""
    print("\n📋 Setting up Labels...")
    
    labels_config = load_labels_config()
    if not labels_config:
        print("❌ No labels configuration found!")
        return
    
    created_count = 0
    existing_count = 0
    failed_count = 0
    total_labels = 0
    
    # Process all categories
    for category, labels in labels_config.items():
        print(f"\n📂 Processing category: {category}")
        for label in labels:
            total_labels += 1
            result = create_label(label)
            if result == "created":
                created_count += 1
            elif result == "exists":
                existing_count += 1
            else:
                failed_count += 1
            
            # Small delay to avoid rate limiting
            time.sleep(0.3)
    
    print(f"\n📊 Labels Setup Summary:")
    print(f"   ✅ Newly created: {created_count}")
    print(f"   ⚠️ Already existed: {existing_count}")
    print(f"   ❌ Failed: {failed_count}")
    print(f"   📊 Total processed: {total_labels}")

def list_existing_labels() -> None:
    """List all existing labels in Chatwoot"""
    print("📋 Listing existing labels...")
    
    url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/labels"
    headers = {"Api-Access-Token": ADMIN_TOKEN}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Handle different response formats
            if isinstance(data, dict) and "payload" in data:
                labels = data["payload"]
            elif isinstance(data, list):
                labels = data
            else:
                labels = []
            
            print(f"\n📊 Found {len(labels)} labels:")
            for label in labels:
                if isinstance(label, dict):
                    print(f"   • {label.get('title', 'Unknown')}")
                else:
                    print(f"   • {label}")
        else:
            print(f"❌ Failed to fetch labels: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error fetching labels: {e}")

def main():
    """Main function"""
    print("🚀 Starting Chatwoot Labels Setup...")
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
            list_existing_labels()
        else:
            print("Usage: python3 scripts/setup_labels.py [list]")
    else:
        setup_labels()
        print("\n🎉 Labels setup completed!")

if __name__ == "__main__":
    main() 