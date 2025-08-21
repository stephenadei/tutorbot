#!/usr/bin/env python3
"""
Quick Coverage Analysis for Tutorbot
Analyzes existing coverage data and provides insights
"""

import os
import re
import ast
from typing import Dict, List, Any
from collections import defaultdict

def analyze_main_py_structure():
    """Analyze main.py structure without importing it"""
    print("🔍 Analyzing main.py structure...")
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse AST
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"❌ Syntax error in main.py: {e}")
        return
    
    # Extract functions and classes
    functions = []
    classes = []
    imports = []
    calls = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append({
                'name': node.name,
                'line': node.lineno,
                'args': [arg.arg for arg in node.args.args],
                'decorators': [d.id for d in node.decorator_list if isinstance(d, ast.Name)]
            })
        elif isinstance(node, ast.ClassDef):
            classes.append({
                'name': node.name,
                'line': node.lineno,
                'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            })
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.append(f"{node.func.value.id}.{node.func.attr}")
    
    print(f"📊 Main.py Analysis:")
    print(f"   Total lines: {len(content.splitlines())}")
    print(f"   File size: {len(content) / 1024:.1f} KB")
    print(f"   Functions: {len(functions)}")
    print(f"   Classes: {len(classes)}")
    print(f"   Imports: {len(imports)}")
    print(f"   Function calls: {len(calls)}")
    
    # Categorize functions
    categorize_functions(functions)
    
    # Find potentially unused functions
    find_unused_functions(functions, calls)
    
    # Analyze function complexity
    analyze_function_complexity(content, functions)

def categorize_functions(functions: List[Dict]):
    """Categorize functions by type"""
    print(f"\n📋 Function Categories:")
    
    categories = {
        'Utility': ['t', 'map_', 'detect_', 'analyze_', 'is_', 'has_', 'get_', 'set_', 'safe_', 'format_', 'parse_'],
        'Handler': ['handle_', 'process_', 'handle_'],
        'Menu': ['show_', 'menu', 'display_'],
        'Flow': ['start_', 'flow', 'begin_', 'end_'],
        'API': ['cw_', 'webhook', 'stripe', 'api_'],
        'Planning': ['plan', 'book', 'suggest', 'slot', 'schedule'],
        'Intake': ['intake', 'prefill', 'collect'],
        'Payment': ['payment', 'stripe', 'create_payment', 'process_payment'],
        'Email': ['email', 'send_', 'mail'],
        'Calendar': ['calendar', 'event', 'booking'],
        'Other': []
    }
    
    categorized = {cat: [] for cat in categories.keys()}
    
    for func in functions:
        categorized_flag = False
        for cat, patterns in categories.items():
            if any(pattern in func['name'] for pattern in patterns):
                categorized[cat].append(func['name'])
                categorized_flag = True
                break
        if not categorized_flag:
            categorized['Other'].append(func['name'])
    
    for cat, funcs in categorized.items():
        if funcs:
            print(f"   {cat}: {len(funcs)} functions")
            if len(funcs) <= 10:  # Show all if 10 or fewer
                for func in funcs:
                    print(f"     - {func}")
            else:  # Show first 5 and last 5
                for func in funcs[:5]:
                    print(f"     - {func}")
                print(f"     ... and {len(funcs) - 10} more ...")
                for func in funcs[-5:]:
                    print(f"     - {func}")

def find_unused_functions(functions: List[Dict], calls: List[str]):
    """Find potentially unused functions"""
    print(f"\n🔍 Unused Function Analysis:")
    
    function_names = [f['name'] for f in functions]
    call_counts = defaultdict(int)
    
    for call in calls:
        call_counts[call] += 1
    
    unused_functions = []
    used_functions = []
    
    for func in functions:
        if func['name'] in call_counts:
            used_functions.append((func['name'], call_counts[func['name']]))
        else:
            unused_functions.append(func['name'])
    
    print(f"   Used functions: {len(used_functions)}")
    print(f"   Potentially unused functions: {len(unused_functions)}")
    
    if unused_functions:
        print(f"\n❌ Potentially unused functions:")
        for func in sorted(unused_functions):
            print(f"   - {func}")
    
    # Show most called functions
    if used_functions:
        print(f"\n🔥 Most called functions:")
        for func, count in sorted(used_functions, key=lambda x: x[1], reverse=True)[:10]:
            print(f"   - {func} (called {count} times)")

def analyze_function_complexity(content: str, functions: List[Dict]):
    """Analyze function complexity"""
    print(f"\n📊 Function Complexity Analysis:")
    
    lines = content.splitlines()
    complex_functions = []
    
    for func in functions:
        # Count lines in function
        start_line = func['line']
        end_line = start_line
        
        # Find function end (simplified)
        brace_count = 0
        for i in range(start_line - 1, len(lines)):
            line = lines[i]
            brace_count += line.count(':')
            brace_count -= line.count('return')
            if brace_count <= 0 and i > start_line:
                end_line = i + 1
                break
        
        func_lines = end_line - start_line + 1
        
        if func_lines > 50:  # Consider functions with >50 lines complex
            complex_functions.append((func['name'], func_lines))
    
    print(f"   Functions with >50 lines: {len(complex_functions)}")
    
    if complex_functions:
        print(f"\n⚠️  Complex functions (consider refactoring):")
        for func, lines in sorted(complex_functions, key=lambda x: x[1], reverse=True)[:10]:
            print(f"   - {func}: {lines} lines")

def analyze_file_sizes():
    """Analyze file sizes in the project"""
    print(f"\n📁 File Size Analysis:")
    
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', 'env', 'node_modules', 'coverage_html', 'htmlcov']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                size = os.path.getsize(filepath)
                python_files.append((filepath, size))
    
    # Sort by size
    python_files.sort(key=lambda x: x[1], reverse=True)
    
    print(f"   Total Python files: {len(python_files)}")
    print(f"   Total size: {sum(size for _, size in python_files) / 1024:.1f} KB")
    
    print(f"\n📦 Largest files:")
    for filepath, size in python_files[:10]:
        print(f"   - {filepath}: {size / 1024:.1f} KB")

def main():
    """Main analysis function"""
    print("🎯 Tutorbot Code Coverage Analysis")
    print("=" * 50)
    
    # Analyze main.py structure
    analyze_main_py_structure()
    
    # Analyze file sizes
    analyze_file_sizes()
    
    print(f"\n✅ Analysis completed!")
    print(f"💡 Recommendations:")
    print(f"   - Consider refactoring large functions")
    print(f"   - Review potentially unused functions")
    print(f"   - Split large files into smaller modules")
    print(f"   - Add unit tests for uncovered code")

if __name__ == "__main__":
    main()

