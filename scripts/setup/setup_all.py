#!/usr/bin/env python3
"""
Master Setup Script for Chatwoot Integration
Runs all setup scripts in the correct order
"""

import os
import sys
import subprocess
import time

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
        "config/conversation_attributes.yaml",
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
        print(f"   python3 scripts/setup_all.py")
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
ADMIN_TOKEN = os.getenv("CW_ADMIN_TOKEN")

def run_script(script_name: str, description: str) -> bool:
    """Run a setup script and return success status"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    script_path = os.path.join(PROJECT_ROOT, "scripts", script_name)
    
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        return False
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=False, 
                              text=True, 
                              cwd=PROJECT_ROOT)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            return True
        else:
            print(f"❌ {description} failed with exit code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def main():
    """Main setup function"""
    print("🎯 Chatwoot Integration Master Setup")
    print(f"   Project root: {PROJECT_ROOT}")
    print(f"   Python: {sys.executable}")
    
    # Check environment variables
    if not all([CW_URL, ACC_ID, ADMIN_TOKEN]):
        print(f"\n❌ Missing required environment variables!")
        print("   Please set: CW_URL, CW_ACC_ID, CW_ADMIN_TOKEN")
        return
    
    print(f"\n✅ Environment variables configured")
    
    # Run setup scripts in order
    success_count = 0
    total_scripts = 2
    
    # 1. Setup custom attributes
    if run_script("setup_attributes.py", "Setting up Custom Attributes"):
        success_count += 1
    
    time.sleep(1)  # Brief pause between scripts
    
    # 2. Setup labels
    if run_script("setup_labels.py", "Setting up Labels"):
        success_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Setup Summary")
    print(f"{'='*60}")
    print(f"   ✅ Successful: {success_count}/{total_scripts}")
    print(f"   ❌ Failed: {total_scripts - success_count}/{total_scripts}")
    
    if success_count == total_scripts:
        print(f"\n🎉 All setup scripts completed successfully!")
        print(f"\n📋 Next Steps:")
        print(f"   1. Configure automation rules manually in Chatwoot")
        print(f"      (see config/automations.yaml for specifications)")
        print(f"   2. Test the bot with dummy conversations")
        print(f"   3. Configure WhatsApp Business API")
        print(f"   4. Set up monitoring dashboards")
    else:
        print(f"\n⚠️ Some setup scripts failed. Please check the logs above.")
        print(f"   You may need to run individual scripts manually:")
        print(f"   python3 scripts/setup_attributes.py")
        print(f"   python3 scripts/setup_labels.py")

if __name__ == "__main__":
    main() 