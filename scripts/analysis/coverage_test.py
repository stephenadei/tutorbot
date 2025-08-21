#!/usr/bin/env python3
"""
Code Coverage Test for main.py
Tests all functions and identifies unused code
"""

import coverage
import sys
import os
import importlib
import inspect
from typing import Dict, List, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_coverage_test():
    """Run comprehensive coverage test on main.py"""
    
    # Start coverage measurement
    cov = coverage.Coverage()
    cov.start()
    
    try:
        # Import main module
        print("🔍 Importing main.py...")
        import main
        
        # Get all functions and classes from main module
        functions = []
        classes = []
        
        for name, obj in inspect.getmembers(main):
            if inspect.isfunction(obj) and obj.__module__ == 'main':
                functions.append((name, obj))
            elif inspect.isclass(obj) and obj.__module__ == 'main':
                classes.append((name, obj))
        
        print(f"📊 Found {len(functions)} functions and {len(classes)} classes")
        
        # Test all functions with mock data
        print("\n🧪 Testing functions...")
        
        # Mock data for testing
        mock_conversation_id = 123
        mock_contact_id = 456
        mock_message = "Test message"
        mock_lang = "nl"
        
        # Test utility functions
        test_utility_functions(main, mock_conversation_id, mock_contact_id, mock_message, mock_lang)
        
        # Test analysis functions
        test_analysis_functions(main, mock_message, mock_conversation_id)
        
        # Test menu functions
        test_menu_functions(main, mock_conversation_id, mock_contact_id, mock_lang)
        
        # Test flow functions
        test_flow_functions(main, mock_conversation_id, mock_contact_id, mock_lang)
        
        print("\n✅ Coverage test completed!")
        
    except Exception as e:
        print(f"❌ Error during coverage test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Stop coverage measurement
        cov.stop()
        cov.save()
        
        # Generate coverage report
        print("\n📈 Generating coverage report...")
        cov.report()
        
        # Generate HTML report
        cov.html_report(directory='coverage_html')
        print("📁 HTML report generated in coverage_html/ directory")
        
        # Get detailed coverage data
        analyze_coverage(cov, functions, classes)

def test_utility_functions(main, cid, contact_id, message, lang):
    """Test utility functions"""
    print("  🔧 Testing utility functions...")
    
    # Test translation function
    try:
        result = main.t("menu_new", lang)
        print(f"    ✅ t() function: {result[:50]}...")
    except Exception as e:
        print(f"    ❌ t() function failed: {e}")
    
    # Test language detection
    try:
        result = main.detect_language_from_message(message)
        print(f"    ✅ detect_language_from_message(): {result}")
    except Exception as e:
        print(f"    ❌ detect_language_from_message() failed: {e}")
    
    # Test topic mapping
    try:
        result = main.map_topic("wiskunde")
        print(f"    ✅ map_topic(): {result}")
    except Exception as e:
        print(f"    ❌ map_topic() failed: {e}")
    
    # Test school level mapping
    try:
        result = main.map_school_level("havo")
        print(f"    ✅ map_school_level(): {result}")
    except Exception as e:
        print(f"    ❌ map_school_level() failed: {e}")

def test_analysis_functions(main, message, conversation_id):
    """Test analysis functions"""
    print("  🧠 Testing analysis functions...")
    
    # Test info request analysis (if OpenAI is available)
    try:
        result = main.analyze_info_request_with_openai(message, conversation_id)
        print(f"    ✅ analyze_info_request_with_openai(): {len(result)} fields")
    except Exception as e:
        print(f"    ⚠️ analyze_info_request_with_openai() failed (expected if no OpenAI): {e}")
    
    # Test first message analysis (if OpenAI is available)
    try:
        result = main.analyze_first_message_with_openai(message, conversation_id)
        print(f"    ✅ analyze_first_message_with_openai(): {len(result)} fields")
    except Exception as e:
        print(f"    ⚠️ analyze_first_message_with_openai() failed (expected if no OpenAI): {e}")

def test_menu_functions(main, cid, contact_id, lang):
    """Test menu functions"""
    print("  📋 Testing menu functions...")
    
    # Test info menu
    try:
        main.show_info_menu(cid, lang)
        print("    ✅ show_info_menu()")
    except Exception as e:
        print(f"    ❌ show_info_menu() failed: {e}")
    
    # Test detailed info menu
    try:
        main.show_detailed_info_menu(cid, lang)
        print("    ✅ show_detailed_info_menu()")
    except Exception as e:
        print(f"    ❌ show_detailed_info_menu() failed: {e}")
    
    # Test prefill action menu
    try:
        main.show_prefill_action_menu(cid, contact_id, lang)
        print("    ✅ show_prefill_action_menu()")
    except Exception as e:
        print(f"    ❌ show_prefill_action_menu() failed: {e}")
    
    # Test segment menu
    try:
        main.show_segment_menu(cid, contact_id, "new", lang)
        print("    ✅ show_segment_menu()")
    except Exception as e:
        print(f"    ❌ show_segment_menu() failed: {e}")

def test_flow_functions(main, cid, contact_id, lang):
    """Test flow functions"""
    print("  🔄 Testing flow functions...")
    
    # Test planning flow
    try:
        main.start_planning_flow(cid, contact_id, lang)
        print("    ✅ start_planning_flow()")
    except Exception as e:
        print(f"    ❌ start_planning_flow() failed: {e}")
    
    # Test intake flow
    try:
        main.start_intake_flow(cid, contact_id, lang)
        print("    ✅ start_intake_flow()")
    except Exception as e:
        print(f"    ❌ start_intake_flow() failed: {e}")

def analyze_coverage(cov, functions, classes):
    """Analyze coverage data and identify unused code"""
    print("\n🔍 Analyzing coverage data...")
    
    # Get coverage data
    analysis = cov.analysis2('main.py')
    statements, excluded, missing, _ = analysis
    
    total_statements = len(statements)
    covered_statements = total_statements - len(missing)
    coverage_percentage = (covered_statements / total_statements * 100) if total_statements > 0 else 0
    
    print(f"\n📊 Coverage Summary:")
    print(f"   Total statements: {total_statements}")
    print(f"   Covered statements: {covered_statements}")
    print(f"   Missing statements: {len(missing)}")
    print(f"   Coverage percentage: {coverage_percentage:.1f}%")
    
    # Identify unused functions
    print(f"\n🔍 Function Analysis:")
    print(f"   Total functions: {len(functions)}")
    
    # Get function line numbers
    unused_functions = []
    for name, func in functions:
        try:
            func_lines = inspect.getsourcelines(func)
            start_line = func_lines[1]
            end_line = start_line + len(func_lines[0]) - 1
            
            # Check if any line in the function is covered
            function_covered = any(start_line <= line <= end_line for line in statements if line not in missing)
            
            if not function_covered:
                unused_functions.append((name, start_line, end_line))
                print(f"   ❌ Unused function: {name} (lines {start_line}-{end_line})")
            else:
                print(f"   ✅ Used function: {name} (lines {start_line}-{end_line})")
                
        except Exception as e:
            print(f"   ⚠️ Could not analyze function {name}: {e}")
    
    # Summary
    print(f"\n📋 Summary:")
    print(f"   Used functions: {len(functions) - len(unused_functions)}")
    print(f"   Unused functions: {len(unused_functions)}")
    
    if unused_functions:
        print(f"\n🗑️ Potential cleanup candidates:")
        for name, start_line, end_line in unused_functions:
            print(f"   - {name} (lines {start_line}-{end_line})")
    else:
        print(f"\n🎉 All functions appear to be used!")

if __name__ == "__main__":
    print("🚀 Starting Code Coverage Test for main.py")
    print("=" * 50)
    
    run_coverage_test()
    
    print("\n" + "=" * 50)
    print("✅ Code coverage test completed!")
    print("📁 Check coverage_html/index.html for detailed HTML report")
