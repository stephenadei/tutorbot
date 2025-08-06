#!/usr/bin/env python3
"""
Project Structure Validation Script
Validates that the project follows the structure defined in .cursorrules
"""

import os
import sys
from typing import List, Dict, Tuple

def ensure_project_root():
    """Ensure we're running from the project root directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    required_files = [
        "main.py",
        "requirements.txt", 
        ".cursorrules"
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
        print(f"   python3 scripts/validate_structure.py")
        sys.exit(1)
    
    if os.getcwd() != project_root:
        print(f"🔄 Changing to project root: {project_root}")
        os.chdir(project_root)
    
    return project_root

# Ensure we're in the right directory before importing anything else
PROJECT_ROOT = ensure_project_root()

def check_directory_structure() -> Tuple[bool, List[str]]:
    """Check if the project structure is correct"""
    print("🔍 Validating project structure...")
    
    # Expected structure
    expected_structure = {
        "config/": [
            "contact_attributes.yaml",
            "conversation_attributes.yaml", 
            "labels_lean.yaml",
            "automations.yaml"
        ],
        "scripts/": [
            "setup/setup_attributes.py",
            "setup/setup_labels.py", 
            "setup/setup_all.py",
            "data/wipe_contacts.py",
            "analysis/validate_structure.py"
        ],
        "docs/": [
            "README.md"
        ],
        "": [  # Root directory files
            "main.py",
            "requirements.txt",
            "docker-compose.yml",
            "Dockerfile",
            "env_example.txt",
            "README.md",
            ".cursorrules"
        ]
    }
    
    issues = []
    all_good = True
    
    for directory, expected_files in expected_structure.items():
        dir_path = os.path.join(PROJECT_ROOT, directory)
        
        # Check if directory exists
        if not os.path.exists(dir_path):
            if directory != "":  # Root directory always exists
                issues.append(f"❌ Missing directory: {directory}")
                all_good = False
                continue
        
        # Check files in directory
        for filename in expected_files:
            file_path = os.path.join(dir_path, filename)
            if not os.path.exists(file_path):
                issues.append(f"❌ Missing file: {os.path.join(directory, filename)}")
                all_good = False
            else:
                print(f"✅ Found: {os.path.join(directory, filename)}")
    
    return all_good, issues

def check_script_validation() -> Tuple[bool, List[str]]:
    """Check if scripts have proper validation"""
    print("\n🔍 Validating script structure...")
    
    script_files = [
        "scripts/setup/setup_attributes.py",
        "scripts/setup/setup_labels.py", 
        "scripts/setup/setup_all.py"
    ]
    
    issues = []
    all_good = True
    
    for script_file in script_files:
        script_path = os.path.join(PROJECT_ROOT, script_file)
        
        if not os.path.exists(script_path):
            issues.append(f"❌ Script not found: {script_file}")
            all_good = False
            continue
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for required components
                checks = [
                    ("ensure_project_root()", "ensure_project_root() function"),
                    ("PROJECT_ROOT = ensure_project_root()", "PROJECT_ROOT assignment"),
                    ("CW_URL = os.getenv", "Environment variable setup"),
                    ("if not all([CW_URL, ACC_ID, ADMIN_TOKEN])", "Environment validation")
                ]
                
                for check_text, description in checks:
                    if check_text not in content:
                        issues.append(f"❌ {script_file}: Missing {description}")
                        all_good = False
                    else:
                        print(f"✅ {script_file}: {description}")
                        
        except Exception as e:
            issues.append(f"❌ Error reading {script_file}: {e}")
            all_good = False
    
    return all_good, issues

def check_no_duplicate_directories() -> Tuple[bool, List[str]]:
    """Check that there are no duplicate directories outside tutorbot/"""
    print("\n🔍 Checking for duplicate directories...")
    
    parent_dir = os.path.dirname(PROJECT_ROOT)
    issues = []
    all_good = True
    
    # Check for common directories that shouldn't exist outside tutorbot/
    problematic_dirs = ["scripts", "config", "docs"]
    
    for dir_name in problematic_dirs:
        problematic_path = os.path.join(parent_dir, dir_name)
        if os.path.exists(problematic_path):
            issues.append(f"❌ Found duplicate directory outside tutorbot/: {dir_name}")
            all_good = False
        else:
            print(f"✅ No duplicate directory: {dir_name}")
    
    return all_good, issues

def main():
    """Main validation function"""
    print("🚀 TutorBot Project Structure Validation")
    print(f"   Project root: {PROJECT_ROOT}")
    print("=" * 60)
    
    # Run all checks
    checks = [
        ("Directory Structure", check_directory_structure),
        ("Script Validation", check_script_validation),
        ("No Duplicate Directories", check_no_duplicate_directories)
    ]
    
    all_passed = True
    all_issues = []
    
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}")
        print("-" * 40)
        
        passed, issues = check_func()
        all_issues.extend(issues)
        
        if not passed:
            all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    if all_passed:
        print("🎉 All checks passed! Project structure is correct.")
        print("\n✅ Project follows .cursorrules guidelines")
        print("✅ All required files and directories exist")
        print("✅ Scripts have proper validation")
        print("✅ No duplicate directories found")
    else:
        print("❌ Some checks failed. Issues found:")
        for issue in all_issues:
            print(f"   {issue}")
        
        print(f"\n💡 Fix the issues above to ensure proper project structure.")
        print(f"   Refer to .cursorrules for guidance.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 