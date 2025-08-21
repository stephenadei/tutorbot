#!/usr/bin/env python3
"""
Git Workflow Helper
Helps manage branches and prevent breaking production deployment
"""

import os
import sys
import subprocess
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

def run_command(cmd, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stdout.strip(), e.stderr.strip()

def get_current_branch():
    """Get current branch name"""
    success, stdout, stderr = run_command("git branch --show-current")
    if success:
        return stdout.strip()
    return None

def get_branch_status():
    """Get status of current branch"""
    success, stdout, stderr = run_command("git status --porcelain")
    if success:
        return stdout.strip()
    return ""

def check_branch_exists(branch_name):
    """Check if a branch exists"""
    success, stdout, stderr = run_command(f"git branch --list {branch_name}")
    return success and stdout.strip() != ""

def create_develop_branch():
    """Create develop branch if it doesn't exist"""
    if not check_branch_exists("develop"):
        print("🌿 Creating develop branch...")
        success, stdout, stderr = run_command("git checkout -b develop")
        if success:
            print("✅ Develop branch created")
            return True
        else:
            print(f"❌ Failed to create develop branch: {stderr}")
            return False
    else:
        print("✅ Develop branch already exists")
        return True

def safe_push_to_master():
    """Safely push to master with confirmation"""
    current_branch = get_current_branch()
    
    if current_branch != "master":
        print(f"❌ You're on branch '{current_branch}', not master!")
        print("💡 Switch to master first: git checkout master")
        return False
    
    # Check for uncommitted changes
    status = get_branch_status()
    if status:
        print("⚠️  You have uncommitted changes:")
        print(status)
        print("\n💡 Commit your changes first: git add . && git commit -m 'message'")
        return False
    
    # Check if behind remote
    success, stdout, stderr = run_command("git status --porcelain --branch")
    if "behind" in stdout:
        print("⚠️  Your local master is behind remote!")
        print("💡 Pull latest changes first: git pull origin master")
        return False
    
    print("🚀 Ready to push to master (this will trigger deployment)")
    print("⚠️  This will deploy to production immediately!")
    
    confirm = input("🤔 Are you sure? (yes/no): ").lower().strip()
    if confirm in ['yes', 'y']:
        success, stdout, stderr = run_command("git push origin master")
        if success:
            print("✅ Successfully pushed to master!")
            print("🚀 Deployment will start automatically...")
            return True
        else:
            print(f"❌ Push failed: {stderr}")
            return False
    else:
        print("❌ Push cancelled")
        return False

def create_feature_branch(feature_name):
    """Create a new feature branch"""
    if not feature_name:
        print("❌ Please provide a feature name")
        return False
    
    # Ensure we're on develop
    current_branch = get_current_branch()
    if current_branch != "develop":
        print(f"⚠️  You're on '{current_branch}', switching to develop...")
        success, stdout, stderr = run_command("git checkout develop")
        if not success:
            print(f"❌ Failed to switch to develop: {stderr}")
            return False
    
    # Create feature branch
    branch_name = f"feature/{feature_name}"
    print(f"🌿 Creating feature branch: {branch_name}")
    
    success, stdout, stderr = run_command(f"git checkout -b {branch_name}")
    if success:
        print(f"✅ Feature branch '{branch_name}' created and checked out")
        return True
    else:
        print(f"❌ Failed to create feature branch: {stderr}")
        return False

def merge_to_develop():
    """Merge current branch to develop"""
    current_branch = get_current_branch()
    
    if current_branch == "develop":
        print("❌ You're already on develop branch")
        return False
    
    if current_branch == "master":
        print("❌ Don't merge master to develop directly")
        return False
    
    print(f"🔄 Merging {current_branch} to develop...")
    
    # Switch to develop
    success, stdout, stderr = run_command("git checkout develop")
    if not success:
        print(f"❌ Failed to switch to develop: {stderr}")
        return False
    
    # Pull latest develop
    success, stdout, stderr = run_command("git pull origin develop")
    if not success:
        print(f"❌ Failed to pull develop: {stderr}")
        return False
    
    # Merge feature branch
    success, stdout, stderr = run_command(f"git merge {current_branch}")
    if success:
        print(f"✅ Successfully merged {current_branch} to develop")
        print("💡 You can now delete the feature branch if needed")
        return True
    else:
        print(f"❌ Merge failed: {stderr}")
        print("💡 Resolve conflicts and try again")
        return False

def show_workflow_help():
    """Show workflow help"""
    print("""
🚀 Git Workflow Commands
=======================

📋 Basic Workflow:
1. Create feature branch:  python3 scripts/git_workflow.py feature <name>
2. Make changes and commit
3. Merge to develop:      python3 scripts/git_workflow.py merge-develop
4. Test on develop
5. Merge to master:       python3 scripts/git_workflow.py deploy

🛡️ Safety Commands:
- Check status:           python3 scripts/git_workflow.py status
- Safe deploy:           python3 scripts/git_workflow.py deploy

🌿 Branch Structure:
- master    → Production (auto-deploy)
- develop   → Testing/Staging
- feature/* → Individual features

💡 Best Practices:
- Never commit directly to master
- Always test on develop first
- Use descriptive commit messages
- Keep feature branches small and focused
""")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        show_workflow_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        current_branch = get_current_branch()
        status = get_branch_status()
        print(f"📍 Current branch: {current_branch}")
        if status:
            print(f"📝 Uncommitted changes:\n{status}")
        else:
            print("✅ Working directory clean")
    
    elif command == "feature" and len(sys.argv) > 2:
        feature_name = sys.argv[2]
        create_feature_branch(feature_name)
    
    elif command == "merge-develop":
        merge_to_develop()
    
    elif command == "deploy":
        safe_push_to_master()
    
    elif command == "setup":
        create_develop_branch()
    
    elif command == "help":
        show_workflow_help()
    
    else:
        print("❌ Unknown command")
        show_workflow_help()

if __name__ == "__main__":
    main() 