#!/usr/bin/env python3
"""
GitHub Secrets Setup Helper
Helps configure GitHub Secrets for TutorBot deployment
"""

import os
import sys
import subprocess
from pathlib import Path

def ensure_project_root():
    """Ensure we're running from the project root directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    required_files = [
        "main.py",
        "requirements.txt", 
        ".github/workflows/deploy.yml"
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
        print(f"   python3 scripts/setup_github_secrets.py")
        sys.exit(1)
    
    if os.getcwd() != project_root:
        print(f"🔄 Changing to project root: {project_root}")
        os.chdir(project_root)
    
    return project_root

# Ensure we're in the right directory
PROJECT_ROOT = ensure_project_root()

def get_ssh_key_content():
    """Get the SSH private key content"""
    ssh_key_path = Path.home() / ".ssh" / "github_actions"
    
    if not ssh_key_path.exists():
        print("❌ SSH key not found. Please run the setup first.")
        return None
    
    with open(ssh_key_path, 'r') as f:
        return f.read().strip()

def get_server_info():
    """Get server information"""
    # Get hostname/IP
    try:
        hostname = subprocess.check_output(['hostname', '-I'], text=True).strip().split()[0]
    except:
        hostname = "YOUR_SERVER_IP"
    
    # Get username
    username = os.getenv('USER', 'stephen')
    
    return {
        'HOST': hostname,
        'USERNAME': username,
        'PORT': '22'
    }

def main():
    """Main function"""
    print("🔧 GitHub Secrets Setup Helper")
    print("=" * 50)
    
    # Get SSH key
    ssh_key = get_ssh_key_content()
    if not ssh_key:
        return
    
    # Get server info
    server_info = get_server_info()
    
    print("\n📋 GitHub Secrets Configuration")
    print("=" * 50)
    print("Go to your GitHub repository:")
    print("Settings → Secrets and variables → Actions")
    print("\nAdd the following secrets:")
    
    print(f"\n🔑 SSH_KEY:")
    print("-" * 20)
    print(ssh_key)
    
    print(f"\n🌐 HOST:")
    print("-" * 20)
    print(server_info['HOST'])
    
    print(f"\n👤 USERNAME:")
    print("-" * 20)
    print(server_info['USERNAME'])
    
    print(f"\n🚪 PORT:")
    print("-" * 20)
    print(server_info['PORT'])
    
    print("\n" + "=" * 50)
    print("✅ After adding these secrets, your deployment should work!")
    print("\n💡 Tips:")
    print("   - Make sure to copy the SSH key exactly as shown")
    print("   - Include the BEGIN and END lines")
    print("   - Don't add extra spaces or newlines")
    print("   - Test the deployment by pushing to master branch")

if __name__ == "__main__":
    main() 