#!/usr/bin/env python3
"""
Simple Code Coverage Test for main.py
Analyzes the file structure and identifies potential unused code
"""

import os
import re
import inspect
from typing import Dict, List, Any

def analyze_main_py_structure():
    """Analyze main.py structure without importing it"""
    
    print("🔍 Analyzing main.py structure...")
    
    # Read main.py file
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all function definitions
    function_pattern = r'^def\s+(\w+)\s*\([^)]*\):'
    functions = re.findall(function_pattern, content, re.MULTILINE)
    
    print(f"📊 Found {len(functions)} functions in main.py")
    
    # Find all function calls
    call_pattern = r'(\w+)\s*\([^)]*\)'
    calls = re.findall(call_pattern, content)
    
    # Filter out built-in functions and common patterns
    built_ins = {'print', 'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 'tuple', 
                 'range', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'reversed', 'sum', 'max', 'min',
                 'abs', 'round', 'divmod', 'pow', 'all', 'any', 'isinstance', 'hasattr', 'getattr',
                 'setattr', 'delattr', 'super', 'open', 'type', 'dir', 'vars', 'locals', 'globals'}
    
    # Remove built-ins and common patterns
    filtered_calls = [call for call in calls if call not in built_ins and not call.startswith('_')]
    
    # Count function calls
    call_counts = {}
    for call in filtered_calls:
        call_counts[call] = call_counts.get(call, 0) + 1
    
    # Analyze function usage
    unused_functions = []
    used_functions = []
    
    for func in functions:
        if func in call_counts:
            used_functions.append((func, call_counts[func]))
        else:
            unused_functions.append(func)
    
    print(f"\n📋 Function Usage Analysis:")
    print(f"   Used functions: {len(used_functions)}")
    print(f"   Unused functions: {len(unused_functions)}")
    
    # Show used functions with call counts
    if used_functions:
        print(f"\n✅ Used functions (with call count):")
        for func, count in sorted(used_functions, key=lambda x: x[1], reverse=True):
            print(f"   - {func} (called {count} times)")
    
    # Show unused functions
    if unused_functions:
        print(f"\n❌ Potentially unused functions:")
        for func in sorted(unused_functions):
            print(f"   - {func}")
    
    # Analyze by function type
    analyze_function_categories(functions, used_functions, unused_functions)
    
    # Find function line numbers
    find_function_line_numbers(content, functions, used_functions)

def analyze_function_categories(functions, used_functions, unused_functions):
    """Analyze functions by category"""
    
    print(f"\n📊 Function Categories:")
    
    # Define categories
    categories = {
        'Utility': ['t', 'map_', 'detect_', 'analyze_', 'is_', 'has_', 'get_', 'set_', 'safe_'],
        'Handler': ['handle_'],
        'Menu': ['show_', 'menu'],
        'Flow': ['start_', 'flow'],
        'API': ['cw', 'webhook', 'stripe'],
        'Planning': ['plan', 'book', 'suggest', 'slot'],
        'Intake': ['intake', 'prefill'],
        'Payment': ['payment', 'stripe', 'create_payment'],
        'Other': []
    }
    
    # Categorize functions
    categorized = {cat: [] for cat in categories.keys()}
    
    for func in functions:
        categorized_flag = False
        for cat, patterns in categories.items():
            if any(pattern in func for pattern in patterns):
                categorized[cat].append(func)
                categorized_flag = True
                break
        if not categorized_flag:
            categorized['Other'].append(func)
    
    # Show categories
    for cat, funcs in categorized.items():
        if funcs:
            used_in_cat = [f for f in funcs if f in [uf[0] for uf in used_functions]]
            unused_in_cat = [f for f in funcs if f in unused_functions]
            print(f"   {cat}: {len(funcs)} total ({len(used_in_cat)} used, {len(unused_in_cat)} unused)")
            
            if unused_in_cat:
                print(f"     Unused: {', '.join(unused_in_cat)}")

def find_function_line_numbers(content, functions, used_functions):
    """Find line numbers for functions"""
    
    print(f"\n📍 Function Line Numbers:")
    
    lines = content.split('\n')
    function_lines = {}
    
    for i, line in enumerate(lines, 1):
        for func in functions:
            if line.strip().startswith(f'def {func}('):
                function_lines[func] = i
                break
    
    # Show line numbers for unused functions
    unused_functions = []
    used_func_names = [uf[0] for uf in used_functions]
    for func in functions:
        if func not in used_func_names:
            unused_functions.append(func)
    
    if unused_functions:
        print(f"\n🗑️ Unused functions with line numbers:")
        for func in sorted(unused_functions):
            line_num = function_lines.get(func, 'unknown')
            print(f"   - {func} (line {line_num})")

def analyze_code_complexity():
    """Analyze code complexity and identify potential issues"""
    
    print(f"\n🔍 Code Complexity Analysis:")
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Count lines
    total_lines = len(lines)
    empty_lines = len([line for line in lines if line.strip() == ''])
    comment_lines = len([line for line in lines if line.strip().startswith('#')])
    code_lines = total_lines - empty_lines - comment_lines
    
    print(f"   Total lines: {total_lines}")
    print(f"   Code lines: {code_lines}")
    print(f"   Comment lines: {comment_lines}")
    print(f"   Empty lines: {empty_lines}")
    
    # Find long functions (more than 50 lines)
    long_functions = []
    current_func = None
    func_start = 0
    
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('def '):
            if current_func:
                func_length = i - func_start
                if func_length > 50:
                    long_functions.append((current_func, func_length, func_start))
            current_func = line.split('(')[0].replace('def ', '').strip()
            func_start = i
    
    # Check last function
    if current_func:
        func_length = len(lines) - func_start
        if func_length > 50:
            long_functions.append((current_func, func_length, func_start))
    
    if long_functions:
        print(f"\n⚠️ Long functions (potential refactoring candidates):")
        for func, length, start_line in sorted(long_functions, key=lambda x: x[1], reverse=True):
            print(f"   - {func} ({length} lines, starts at line {start_line})")

def main():
    """Main analysis function"""
    
    print("🚀 Starting Simple Code Coverage Analysis for main.py")
    print("=" * 60)
    
    if not os.path.exists('main.py'):
        print("❌ main.py not found in current directory")
        return
    
    # Analyze structure
    analyze_main_py_structure()
    
    # Analyze complexity
    analyze_code_complexity()
    
    print("\n" + "=" * 60)
    print("✅ Simple code coverage analysis completed!")
    print("\n💡 Recommendations:")
    print("   - Review unused functions for potential removal")
    print("   - Consider refactoring long functions")
    print("   - Add more comments to complex sections")
    print("   - Consider splitting main.py into smaller modules")

if __name__ == "__main__":
    main()
