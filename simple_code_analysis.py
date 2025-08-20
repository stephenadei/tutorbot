#!/usr/bin/env python3
"""
Simple Code Analysis for Tutorbot
Basic analysis without complex AST parsing
"""

import os
import re
from typing import Dict, List, Any
from collections import defaultdict

def analyze_main_py():
    """Analyze main.py using regex patterns"""
    print("🔍 Analyzing main.py...")
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.splitlines()
    
    # Find function definitions
    function_pattern = r'^def\s+(\w+)\s*\([^)]*\):'
    functions = re.findall(function_pattern, content, re.MULTILINE)
    
    # Find class definitions
    class_pattern = r'^class\s+(\w+)'
    classes = re.findall(class_pattern, content, re.MULTILINE)
    
    # Find imports
    import_pattern = r'^(?:from\s+(\w+)\s+import|import\s+(\w+))'
    imports = re.findall(import_pattern, content, re.MULTILINE)
    imports = [imp[0] if imp[0] else imp[1] for imp in imports if any(imp)]
    
    # Find function calls (simplified)
    call_pattern = r'(\w+)\s*\([^)]*\)'
    calls = re.findall(call_pattern, content)
    
    # Filter out built-ins and common patterns
    built_ins = {
        'print', 'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 'tuple',
        'range', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'reversed', 'sum', 'max', 'min',
        'abs', 'round', 'divmod', 'pow', 'all', 'any', 'isinstance', 'hasattr', 'getattr',
        'setattr', 'delattr', 'super', 'open', 'type', 'dir', 'vars', 'locals', 'globals',
        'format', 'join', 'split', 'strip', 'replace', 'find', 'index', 'count', 'startswith',
        'endswith', 'lower', 'upper', 'title', 'capitalize', 'isalpha', 'isdigit', 'isalnum',
        'append', 'extend', 'insert', 'remove', 'pop', 'clear', 'copy', 'get', 'update',
        'keys', 'values', 'items', 'add', 'discard', 'union', 'intersection', 'difference'
    }
    
    filtered_calls = [call for call in calls if call not in built_ins and not call.startswith('_')]
    
    # Count function calls
    call_counts = defaultdict(int)
    for call in filtered_calls:
        call_counts[call] += 1
    
    print(f"📊 Main.py Analysis:")
    print(f"   Total lines: {len(lines)}")
    print(f"   File size: {len(content) / 1024:.1f} KB")
    print(f"   Functions: {len(functions)}")
    print(f"   Classes: {len(classes)}")
    print(f"   Imports: {len(imports)}")
    print(f"   Function calls: {len(filtered_calls)}")
    
    # Categorize functions
    categorize_functions(functions)
    
    # Find potentially unused functions
    find_unused_functions(functions, call_counts)
    
    # Analyze function complexity
    analyze_function_complexity(content, functions)
    
    # Show most called functions
    show_most_called_functions(call_counts)

def categorize_functions(functions: List[str]):
    """Categorize functions by type"""
    print(f"\n📋 Function Categories:")
    
    categories = {
        'Utility': ['t', 'map_', 'detect_', 'analyze_', 'is_', 'has_', 'get_', 'set_', 'safe_', 'format_', 'parse_'],
        'Handler': ['handle_', 'process_'],
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
            if any(pattern in func for pattern in patterns):
                categorized[cat].append(func)
                categorized_flag = True
                break
        if not categorized_flag:
            categorized['Other'].append(func)
    
    for cat, funcs in categorized.items():
        if funcs:
            print(f"   {cat}: {len(funcs)} functions")
            if len(funcs) <= 8:  # Show all if 8 or fewer
                for func in funcs:
                    print(f"     - {func}")
            else:  # Show first 4 and last 4
                for func in funcs[:4]:
                    print(f"     - {func}")
                print(f"     ... and {len(funcs) - 8} more ...")
                for func in funcs[-4:]:
                    print(f"     - {func}")

def find_unused_functions(functions: List[str], call_counts: Dict[str, int]):
    """Find potentially unused functions"""
    print(f"\n🔍 Unused Function Analysis:")
    
    unused_functions = []
    used_functions = []
    
    for func in functions:
        if func in call_counts:
            used_functions.append((func, call_counts[func]))
        else:
            unused_functions.append(func)
    
    print(f"   Used functions: {len(used_functions)}")
    print(f"   Potentially unused functions: {len(unused_functions)}")
    
    if unused_functions:
        print(f"\n❌ Potentially unused functions:")
        for func in sorted(unused_functions):
            print(f"   - {func}")

def show_most_called_functions(call_counts: Dict[str, int]):
    """Show most called functions"""
    if call_counts:
        print(f"\n🔥 Most called functions:")
        for func, count in sorted(call_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
            print(f"   - {func} (called {count} times)")

def analyze_function_complexity(content: str, functions: List[str]):
    """Analyze function complexity"""
    print(f"\n📊 Function Complexity Analysis:")
    
    lines = content.splitlines()
    complex_functions = []
    
    for func in functions:
        # Find function start
        func_pattern = rf'^def\s+{re.escape(func)}\s*\([^)]*\):'
        for i, line in enumerate(lines):
            if re.match(func_pattern, line):
                start_line = i + 1
                # Count lines until next function or end
                func_lines = 0
                for j in range(start_line, len(lines)):
                    if lines[j].strip().startswith('def ') and j > start_line:
                        break
                    if lines[j].strip() and not lines[j].strip().startswith('#'):
                        func_lines += 1
                
                if func_lines > 30:  # Consider functions with >30 lines complex
                    complex_functions.append((func, func_lines))
                break
    
    print(f"   Functions with >30 lines: {len(complex_functions)}")
    
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
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', 'env', 'node_modules', 'coverage_html', 'htmlcov', 'tutorbot_env']]
        
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

def analyze_coverage_data():
    """Analyze existing coverage data"""
    print(f"\n📈 Coverage Data Analysis:")
    
    if os.path.exists('.coverage'):
        print("   ✅ Coverage data file found (.coverage)")
        
        # Try to read coverage data
        try:
            import coverage
            cov = coverage.Coverage()
            cov.load()
            
            # Get summary
            summary = cov.get_data().summary()
            total_lines = sum(summary.values())
            covered_lines = sum(1 for count in summary.values() if count > 0)
            
            if total_lines > 0:
                coverage_percentage = (covered_lines / total_lines) * 100
                print(f"   Total executable lines: {total_lines}")
                print(f"   Covered lines: {covered_lines}")
                print(f"   Coverage percentage: {coverage_percentage:.1f}%")
            else:
                print("   No coverage data available")
                
        except Exception as e:
            print(f"   ⚠️  Could not read coverage data: {e}")
    else:
        print("   ❌ No coverage data file found")

def main():
    """Main analysis function"""
    print("🎯 Tutorbot Simple Code Analysis")
    print("=" * 50)
    
    # Analyze main.py
    analyze_main_py()
    
    # Analyze file sizes
    analyze_file_sizes()
    
    # Analyze coverage data
    analyze_coverage_data()
    
    print(f"\n✅ Analysis completed!")
    print(f"💡 Recommendations:")
    print(f"   - Consider refactoring large functions")
    print(f"   - Review potentially unused functions")
    print(f"   - Split large files into smaller modules")
    print(f"   - Add unit tests for uncovered code")
    print(f"   - Consider breaking main.py into smaller modules")

if __name__ == "__main__":
    main()
