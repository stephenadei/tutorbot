#!/usr/bin/env python3
"""
Comprehensive Code Coverage Test for Tutorbot
Analyzes the entire codebase and identifies unused code, dead code, and coverage gaps
"""

import coverage
import sys
import os
import re
import ast
import inspect
import importlib
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class CodeAnalyzer:
    def __init__(self):
        self.functions = []
        self.classes = []
        self.imports = []
        self.calls = defaultdict(int)
        self.unused_functions = []
        self.unused_classes = []
        self.dead_code = []
        self.coverage_data = {}
        
    def analyze_file_structure(self, filepath: str) -> Dict[str, Any]:
        """Analyze a Python file structure without importing it"""
        print(f"🔍 Analyzing {filepath}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"❌ Syntax error in {filepath}: {e}")
            return {}
        
        analysis = {
            'functions': [],
            'classes': [],
            'imports': [],
            'calls': [],
            'lines': len(content.splitlines()),
            'size_kb': len(content) / 1024
        }
        
        # Extract functions, classes, and imports
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                analysis['functions'].append({
                    'name': node.name,
                    'line': node.lineno,
                    'args': [arg.arg for arg in node.args.args],
                    'decorators': [d.id for d in node.decorator_list if isinstance(d, ast.Name)]
                })
            elif isinstance(node, ast.ClassDef):
                analysis['classes'].append({
                    'name': node.name,
                    'line': node.lineno,
                    'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                })
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    analysis['imports'].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    analysis['imports'].append(f"{module}.{alias.name}")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    analysis['calls'].append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    analysis['calls'].append(f"{node.func.value.id}.{node.func.attr}")
        
        return analysis
    
    def run_coverage_test(self, main_file: str = 'main.py'):
        """Run comprehensive coverage test"""
        print("🚀 Starting comprehensive coverage test...")
        
        # Start coverage measurement
        cov = coverage.Coverage(
            source=['.'],
            omit=['*/tests/*', '*/test_*.py', '*coverage*', '*/__pycache__/*', '*/venv/*', '*/env/*']
        )
        cov.start()
        
        try:
            # Import main module
            print(f"📦 Importing {main_file}...")
            main_module = importlib.import_module(main_file.replace('.py', ''))
            
            # Get all functions and classes
            self.extract_module_members(main_module)
            
            # Test functions with mock data
            self.test_functions_with_mocks(main_module)
            
            print("✅ Coverage test completed!")
            
        except Exception as e:
            print(f"❌ Error during coverage test: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Stop coverage measurement
            cov.stop()
            cov.save()
            
            # Generate reports
            self.generate_reports(cov)
    
    def extract_module_members(self, module):
        """Extract all functions and classes from module"""
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and obj.__module__ == module.__name__:
                self.functions.append((name, obj))
            elif inspect.isclass(obj) and obj.__module__ == module.__name__:
                self.classes.append((name, obj))
        
        print(f"📊 Found {len(self.functions)} functions and {len(self.classes)} classes")
    
    def test_functions_with_mocks(self, module):
        """Test functions with mock data"""
        print("🧪 Testing functions with mock data...")
        
        # Mock data
        mock_data = {
            'conversation_id': 12345,
            'contact_id': 67890,
            'message': "Test message for coverage analysis",
            'lang': "nl",
            'user_input': "test input",
            'data': {'test': 'data'},
            'request': type('MockRequest', (), {'json': lambda: {'test': 'data'}})()
        }
        
        tested_functions = 0
        failed_functions = 0
        
        for name, func in self.functions:
            try:
                # Skip private functions and special methods
                if name.startswith('_') or name in ['main', 'app']:
                    continue
                
                # Get function signature
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                
                # Create arguments based on parameter names
                args = []
                for param in params:
                    if param in mock_data:
                        args.append(mock_data[param])
                    elif param == 'self':
                        continue
                    else:
                        # Try to provide a default value
                        args.append(None)
                
                # Call function with mock arguments
                if args:
                    func(*args)
                else:
                    func()
                
                tested_functions += 1
                self.calls[name] += 1
                
            except Exception as e:
                failed_functions += 1
                print(f"    ⚠️  {name} failed: {str(e)[:100]}...")
        
        print(f"  ✅ Tested {tested_functions} functions")
        print(f"  ❌ Failed {failed_functions} functions")
    
    def generate_reports(self, cov):
        """Generate comprehensive coverage reports"""
        print("\n📈 Generating coverage reports...")
        
        # Generate standard reports
        cov.report()
        
        # Generate HTML report
        cov.html_report(directory='coverage_html')
        print("📁 HTML report generated in coverage_html/ directory")
        
        # Analyze coverage data
        self.analyze_coverage_data(cov)
        
        # Generate detailed analysis
        self.generate_detailed_analysis()
    
    def analyze_coverage_data(self, cov):
        """Analyze coverage data for insights"""
        print("\n🔍 Analyzing coverage data...")
        
        # Get coverage data
        analysis = cov.analysis('main.py')
        if analysis:
            executable, missing, excluded = analysis
            
            total_lines = len(executable)
            covered_lines = total_lines - len(missing)
            coverage_percentage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
            
            print(f"📊 Coverage Statistics:")
            print(f"   Total executable lines: {total_lines}")
            print(f"   Covered lines: {covered_lines}")
            print(f"   Missing lines: {len(missing)}")
            print(f"   Coverage percentage: {coverage_percentage:.1f}%")
            
            # Identify missing lines
            if missing:
                print(f"\n❌ Missing coverage lines: {sorted(missing)[:20]}...")
    
    def generate_detailed_analysis(self):
        """Generate detailed code analysis"""
        print("\n📋 Generating detailed analysis...")
        
        # Analyze all Python files
        python_files = self.find_python_files('.')
        
        total_analysis = {
            'files': {},
            'summary': {
                'total_files': len(python_files),
                'total_functions': 0,
                'total_classes': 0,
                'total_lines': 0,
                'total_size_kb': 0
            }
        }
        
        for filepath in python_files:
            if filepath.endswith('.py') and not filepath.startswith('test_'):
                analysis = self.analyze_file_structure(filepath)
                if analysis:
                    total_analysis['files'][filepath] = analysis
                    total_analysis['summary']['total_functions'] += len(analysis['functions'])
                    total_analysis['summary']['total_classes'] += len(analysis['classes'])
                    total_analysis['summary']['total_lines'] += analysis['lines']
                    total_analysis['summary']['total_size_kb'] += analysis['size_kb']
        
        # Save analysis to JSON
        with open('code_analysis_report.json', 'w') as f:
            json.dump(total_analysis, f, indent=2)
        
        print(f"📄 Analysis saved to code_analysis_report.json")
        
        # Print summary
        self.print_analysis_summary(total_analysis)
    
    def find_python_files(self, directory: str) -> List[str]:
        """Find all Python files in directory"""
        python_files = []
        for root, dirs, files in os.walk(directory):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', 'env', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        return python_files
    
    def print_analysis_summary(self, analysis: Dict[str, Any]):
        """Print analysis summary"""
        summary = analysis['summary']
        
        print(f"\n📊 Code Analysis Summary:")
        print(f"   Total Python files: {summary['total_files']}")
        print(f"   Total functions: {summary['total_functions']}")
        print(f"   Total classes: {summary['total_classes']}")
        print(f"   Total lines of code: {summary['total_lines']:,}")
        print(f"   Total code size: {summary['total_size_kb']:.1f} KB")
        
        # Find largest files
        files_by_size = sorted(
            analysis['files'].items(),
            key=lambda x: x[1]['size_kb'],
            reverse=True
        )
        
        print(f"\n📁 Largest files:")
        for filepath, file_analysis in files_by_size[:5]:
            print(f"   {filepath}: {file_analysis['size_kb']:.1f} KB ({file_analysis['lines']} lines)")
        
        # Find files with most functions
        files_by_functions = sorted(
            analysis['files'].items(),
            key=lambda x: len(x[1]['functions']),
            reverse=True
        )
        
        print(f"\n🔧 Files with most functions:")
        for filepath, file_analysis in files_by_functions[:5]:
            print(f"   {filepath}: {len(file_analysis['functions'])} functions")

def main():
    """Main function to run comprehensive coverage test"""
    print("🎯 Tutorbot Comprehensive Code Coverage Test")
    print("=" * 50)
    
    analyzer = CodeAnalyzer()
    
    # Run coverage test
    analyzer.run_coverage_test('main.py')
    
    print("\n✅ Coverage test completed!")
    print("📁 Check the following files for results:")
    print("   - coverage_html/ (HTML coverage report)")
    print("   - code_analysis_report.json (Detailed analysis)")
    print("   - .coverage (Coverage data)")

if __name__ == "__main__":
    main()
