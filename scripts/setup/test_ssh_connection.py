#!/usr/bin/env python3
"""
Test SSH Connection
Simulates GitHub Actions SSH connection to debug issues
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def ensure_project_root():
    """Ensure we're running from the project root directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    if os.getcwd() != project_root:
        print(f"🔄 Changing to project root: {project_root}")
        os.chdir(project_root)
    
    return project_root

PROJECT_ROOT = ensure_project_root()

def test_ssh_connection():
    """Test SSH connection using the GitHub Actions key"""
    print("🔧 Testing SSH Connection (GitHub Actions Style)")
    print("=" * 50)
    
    # Get the private key
    ssh_key_path = Path.home() / ".ssh" / "github_actions"
    
    if not ssh_key_path.exists():
        print("❌ SSH key not found: ~/.ssh/github_actions")
        return False
    
    # Read the private key
    with open(ssh_key_path, 'r') as f:
        private_key = f.read().strip()
    
    print(f"✅ Found SSH key: {ssh_key_path}")
    print(f"📏 Key length: {len(private_key)} characters")
    
    # Create a temporary key file (like GitHub Actions does)
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.key') as temp_key:
        temp_key.write(private_key)
        temp_key_path = temp_key.name
    
    try:
        # Set proper permissions
        os.chmod(temp_key_path, 0o600)
        
        # Test SSH connection
        print("\n🔍 Testing SSH connection...")
        cmd = [
            'ssh',
            '-i', temp_key_path,
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'LogLevel=DEBUG3',
            'stephen@localhost',
            'echo "SSH connection successful"'
        ]
        
        print(f"🚀 Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"\n📊 Exit code: {result.returncode}")
        
        if result.stdout:
            print(f"✅ STDOUT: {result.stdout.strip()}")
        
        if result.stderr:
            print(f"⚠️  STDERR: {result.stderr.strip()}")
        
        if result.returncode == 0:
            print("\n🎉 SSH connection successful!")
            return True
        else:
            print("\n❌ SSH connection failed!")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n⏰ SSH connection timed out!")
        return False
    except Exception as e:
        print(f"\n💥 Error: {e}")
        return False
    finally:
        # Clean up temporary key file
        try:
            os.unlink(temp_key_path)
        except:
            pass

def check_ssh_config():
    """Check SSH configuration"""
    print("\n🔍 Checking SSH Configuration")
    print("=" * 30)
    
    # Check SSH service
    try:
        result = subprocess.run(['systemctl', 'is-active', 'ssh'], 
                              capture_output=True, text=True)
        print(f"🔧 SSH Service: {result.stdout.strip()}")
    except:
        print("🔧 SSH Service: Could not check")
    
    # Check SSH port
    try:
        result = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True)
        if ':22 ' in result.stdout:
            print("🚪 SSH Port 22: Listening")
        else:
            print("🚪 SSH Port 22: Not listening")
    except:
        print("🚪 SSH Port 22: Could not check")
    
    # Check authorized_keys permissions
    auth_keys_path = Path.home() / ".ssh" / "authorized_keys"
    if auth_keys_path.exists():
        stat = auth_keys_path.stat()
        print(f"📁 authorized_keys permissions: {oct(stat.st_mode)[-3:]}")
    else:
        print("📁 authorized_keys: Not found")

def main():
    """Main function"""
    print("🚀 SSH Connection Test for GitHub Actions")
    print("=" * 50)
    
    # Check SSH config
    check_ssh_config()
    
    # Test connection
    success = test_ssh_connection()
    
    if success:
        print("\n✅ All tests passed! SSH should work with GitHub Actions.")
    else:
        print("\n❌ SSH connection failed. Check the configuration.")
        print("\n💡 Troubleshooting tips:")
        print("   1. Verify the SSH key in GitHub Secrets")
        print("   2. Check server SSH configuration")
        print("   3. Ensure firewall allows SSH connections")

if __name__ == "__main__":
    main() 