#!/usr/bin/env python3
"""
Targeted Code Coverage Test for main.py
Tests specific functions and identifies unused code
"""

import coverage
import sys
import os
import inspect
from typing import Dict, List, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_targeted_coverage_test():
    """Run targeted coverage test on main.py"""
    
    # Start coverage measurement
    cov = coverage.Coverage()
    cov.start()
    
    try:
        # Import main module
        print("🔍 Importing main.py...")
        import main
        
        # Test specific functions we know exist
        print("\n🧪 Testing specific functions...")
        
        # Mock data
        mock_cid = 123
        mock_contact_id = 456
        mock_message = "Test message"
        mock_lang = "nl"
        mock_msg_content = "test"
        
        # Test utility functions
        test_utility_functions(main, mock_message, mock_lang)
        
        # Test mapping functions
        test_mapping_functions(main)
        
        # Test analysis functions
        test_analysis_functions(main, mock_message, mock_cid)
        
        # Test menu functions (these will fail without proper setup, but we can test imports)
        test_menu_functions(main, mock_cid, mock_contact_id, mock_lang)
        
        # Test flow functions
        test_flow_functions(main, mock_cid, mock_contact_id, mock_lang)
        
        # Test handler functions
        test_handler_functions(main, mock_cid, mock_contact_id, mock_msg_content, mock_lang)
        
        print("\n✅ Targeted coverage test completed!")
        
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
        
        # Analyze coverage
        analyze_targeted_coverage(cov)

def test_utility_functions(main, message, lang):
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

def test_mapping_functions(main):
    """Test mapping functions"""
    print("  🗺️ Testing mapping functions...")
    
    # Test topic mapping
    try:
        result = main.map_topic("wiskunde")
        print(f"    ✅ map_topic('wiskunde'): {result}")
    except Exception as e:
        print(f"    ❌ map_topic() failed: {e}")
    
    # Test school level mapping
    try:
        result = main.map_school_level("havo")
        print(f"    ✅ map_school_level('havo'): {result}")
    except Exception as e:
        print(f"    ❌ map_school_level() failed: {e}")

def test_analysis_functions(main, message, conversation_id):
    """Test analysis functions"""
    print("  🧠 Testing analysis functions...")
    
    # Test info request analysis
    try:
        result = main.analyze_info_request_with_openai(message, conversation_id)
        print(f"    ✅ analyze_info_request_with_openai(): {len(result)} fields")
    except Exception as e:
        print(f"    ⚠️ analyze_info_request_with_openai() failed (expected if no OpenAI): {e}")
    
    # Test first message analysis
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

def test_handler_functions(main, cid, contact_id, msg_content, lang):
    """Test handler functions"""
    print("  🎮 Testing handler functions...")
    
    # Test prefill confirmation handler
    try:
        main.handle_prefill_confirmation(cid, contact_id, msg_content, lang)
        print("    ✅ handle_prefill_confirmation()")
    except Exception as e:
        print(f"    ❌ handle_prefill_confirmation() failed: {e}")
    
    # Test info menu selection handler
    try:
        main.handle_info_menu_selection(cid, contact_id, msg_content, lang)
        print("    ✅ handle_info_menu_selection()")
    except Exception as e:
        print(f"    ❌ handle_info_menu_selection() failed: {e}")
    
    # Test prefill action selection handler
    try:
        main.handle_prefill_action_selection(cid, contact_id, msg_content, lang)
        print("    ✅ handle_prefill_action_selection()")
    except Exception as e:
        print(f"    ❌ handle_prefill_action_selection() failed: {e}")

def analyze_targeted_coverage(cov):
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
    
    # Get all functions from main module
    functions = []
    for name, obj in inspect.getmembers(main):
        if inspect.isfunction(obj) and obj.__module__ == 'main':
            functions.append((name, obj))
    
    print(f"\n🔍 Function Analysis:")
    print(f"   Total functions: {len(functions)}")
    
    # Analyze each function
    unused_functions = []
    used_functions = []
    
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
                used_functions.append((name, start_line, end_line))
                print(f"   ✅ Used function: {name} (lines {start_line}-{end_line})")
                
        except Exception as e:
            print(f"   ⚠️ Could not analyze function {name}: {e}")
    
    # Summary
    print(f"\n📋 Summary:")
    print(f"   Used functions: {len(used_functions)}")
    print(f"   Unused functions: {len(unused_functions)}")
    
    if unused_functions:
        print(f"\n🗑️ Potential cleanup candidates:")
        for name, start_line, end_line in unused_functions:
            print(f"   - {name} (lines {start_line}-{end_line})")
        
        # Group by function type
        print(f"\n📊 Unused functions by category:")
        utility_functions = [f for f in unused_functions if any(keyword in f[0].lower() for keyword in ['map', 'detect', 'analyze'])]
        handler_functions = [f for f in unused_functions if 'handle' in f[0].lower()]
        menu_functions = [f for f in unused_functions if 'menu' in f[0].lower()]
        flow_functions = [f for f in unused_functions if 'flow' in f[0].lower()]
        other_functions = [f for f in unused_functions if f not in utility_functions + handler_functions + menu_functions + flow_functions]
        
        if utility_functions:
            print(f"   🔧 Utility functions: {len(utility_functions)}")
        if handler_functions:
            print(f"   🎮 Handler functions: {len(handler_functions)}")
        if menu_functions:
            print(f"   📋 Menu functions: {len(menu_functions)}")
        if flow_functions:
            print(f"   🔄 Flow functions: {len(flow_functions)}")
        if other_functions:
            print(f"   🔍 Other functions: {len(other_functions)}")
    else:
        print(f"\n🎉 All functions appear to be used!")

if __name__ == "__main__":
    print("🚀 Starting Targeted Code Coverage Test for main.py")
    print("=" * 60)
    
    run_targeted_coverage_test()
    
    print("\n" + "=" * 60)
    print("✅ Targeted code coverage test completed!")
    print("📁 Check coverage_html/index.html for detailed HTML report")
