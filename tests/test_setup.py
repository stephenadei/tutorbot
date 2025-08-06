#!/usr/bin/env python3
"""
Test setup verification script for TutorBot
"""

import os
import sys
import importlib

def check_imports():
    """Check if all required modules can be imported"""
    print("🔍 Checking imports...")
    
    required_modules = [
        'flask',
        'openai',
        'requests',
        'json',
        'datetime',
        'zoneinfo',
        're',
        'hmac',
        'hashlib'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            missing_modules.append(module)
    
    return len(missing_modules) == 0

def check_project_structure():
    """Check if project structure is correct"""
    print("\n📁 Checking project structure...")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'tests/__init__.py',
        'tests/test_main.py',
        'tests/test_config.py',
        'run_tests.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def check_test_imports():
    """Check if test modules can be imported"""
    print("\n🧪 Checking test imports...")
    
    try:
        # Add project root to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Try to import test modules
        from tests.test_config import setup_test_environment, cleanup_test_environment
        print("✅ tests.test_config")
        
        # Try to import main test module (this will fail if main.py has issues)
        try:
            from tests.test_main import TestTranslation
            print("✅ tests.test_main")
        except Exception as e:
            print(f"⚠️ tests.test_main: {e}")
            print("   This is expected if main.py has dependencies not available in test environment")
        
        return True
    except Exception as e:
        print(f"❌ Test imports failed: {e}")
        return False

def check_environment():
    """Check environment setup"""
    print("\n🌍 Checking environment...")
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major >= 3 and python_version.minor >= 8:
        print("✅ Python version is compatible")
    else:
        print("❌ Python 3.8+ required")
        return False
    
    # Check current directory
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    # Check if we're in the project root
    if os.path.exists('main.py'):
        print("✅ In project root directory")
    else:
        print("❌ Not in project root directory")
        return False
    
    return True

def run_basic_tests():
    """Run a few basic tests to verify setup"""
    print("\n🧪 Running basic tests...")
    
    try:
        # Setup test environment
        from tests.test_config import setup_test_environment, cleanup_test_environment
        setup_test_environment()
        
        # Test translation function
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from main import t
        
        result = t("greeting_with_name", "nl", name="Test")
        if "Test" in result:
            print("✅ Translation function works")
        else:
            print("❌ Translation function failed")
            return False
        
        # Test utility functions
        from main import is_existing_customer, has_completed_intake
        
        # Test existing customer detection
        contact_attrs = {"is_student": True, "has_paid_lesson": True}
        if is_existing_customer(contact_attrs):
            print("✅ Existing customer detection works")
        else:
            print("❌ Existing customer detection failed")
            return False
        
        # Test intake completion check
        conv_attrs = {"intake_completed": True}
        if has_completed_intake(conv_attrs):
            print("✅ Intake completion check works")
        else:
            print("❌ Intake completion check failed")
            return False
        
        cleanup_test_environment()
        return True
        
    except Exception as e:
        print(f"❌ Basic tests failed: {e}")
        return False

def main():
    """Main verification function"""
    print("🔧 TutorBot Test Setup Verification")
    print("=" * 50)
    
    checks = [
        ("Environment", check_environment),
        ("Project Structure", check_project_structure),
        ("Required Imports", check_imports),
        ("Test Imports", check_test_imports),
        ("Basic Tests", run_basic_tests)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} check failed with exception: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All checks passed! Test environment is ready.")
        print("\nYou can now run tests with:")
        print("  python run_tests.py")
        print("  python run_tests.py --list-categories")
        print("  python run_tests.py --category translation")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("  1. Install missing dependencies: pip install -r requirements.txt")
        print("  2. Ensure you're in the project root directory")
        print("  3. Check Python version (3.8+ required)")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 