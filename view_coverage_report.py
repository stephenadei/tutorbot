#!/usr/bin/env python3
"""
View Coverage Report for Tutorbot
Opens the HTML coverage report and provides a summary
"""

import os
import webbrowser
import json
from pathlib import Path

def open_coverage_report():
    """Open the HTML coverage report in browser"""
    coverage_dir = Path('coverage_html')
    index_file = coverage_dir / 'index.html'
    
    if index_file.exists():
        print("🌐 Opening coverage report in browser...")
        webbrowser.open(f'file://{index_file.absolute()}')
        print(f"✅ Coverage report opened: {index_file.absolute()}")
    else:
        print("❌ Coverage report not found. Run coverage test first.")

def show_coverage_summary():
    """Show a summary of coverage results"""
    print("\n📊 Coverage Summary:")
    print("=" * 40)
    
    # Check if coverage data exists
    if os.path.exists('.coverage'):
        print("✅ Coverage data found (.coverage)")
    else:
        print("❌ No coverage data found")
        return
    
    # Check if HTML report exists
    if os.path.exists('coverage_html/index.html'):
        print("✅ HTML report generated (coverage_html/index.html)")
    else:
        print("❌ HTML report not found")
        return
    
    # Try to read status.json for summary
    status_file = Path('coverage_html/status.json')
    if status_file.exists():
        try:
            with open(status_file, 'r') as f:
                status = json.load(f)
            
            print(f"\n📈 Coverage Statistics:")
            total_lines = 0
            covered_lines = 0
            
            for file_info in status.values():
                if isinstance(file_info, dict) and 'coverage' in file_info:
                    total_lines += file_info.get('total_lines', 0)
                    covered_lines += file_info.get('covered_lines', 0)
            
            if total_lines > 0:
                coverage_percentage = (covered_lines / total_lines) * 100
                print(f"   Total executable lines: {total_lines:,}")
                print(f"   Covered lines: {covered_lines:,}")
                print(f"   Missing lines: {total_lines - covered_lines:,}")
                print(f"   Coverage percentage: {coverage_percentage:.1f}%")
                
                if coverage_percentage < 20:
                    print("   🚨 Very low coverage - needs immediate attention!")
                elif coverage_percentage < 50:
                    print("   ⚠️  Low coverage - should be improved")
                elif coverage_percentage < 80:
                    print("   ✅ Good coverage - room for improvement")
                else:
                    print("   🎉 Excellent coverage!")
            
        except Exception as e:
            print(f"   ⚠️  Could not read status file: {e}")
    
    print(f"\n📁 Files analyzed:")
    coverage_dir = Path('coverage_html')
    html_files = list(coverage_dir.glob('*.html'))
    py_files = [f for f in html_files if f.name.endswith('_py.html')]
    
    print(f"   Python files: {len(py_files)}")
    
    # Show largest files
    print(f"\n📦 Largest files in coverage:")
    file_sizes = []
    for py_file in py_files:
        if py_file.exists():
            size = py_file.stat().st_size
            file_sizes.append((py_file.name, size))
    
    file_sizes.sort(key=lambda x: x[1], reverse=True)
    for name, size in file_sizes[:5]:
        print(f"   - {name}: {size / 1024:.1f} KB")

def main():
    """Main function"""
    print("🎯 Tutorbot Coverage Report Viewer")
    print("=" * 40)
    
    # Show summary
    show_coverage_summary()
    
    # Ask if user wants to open report
    print(f"\n🌐 Options:")
    print("   1. Open HTML coverage report in browser")
    print("   2. View coverage summary only")
    print("   3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        open_coverage_report()
    elif choice == '2':
        print("✅ Summary displayed above")
    elif choice == '3':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
