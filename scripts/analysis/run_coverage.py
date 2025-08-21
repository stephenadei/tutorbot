#!/usr/bin/env python3
"""
Quick Coverage Runner for Tutorbot
Simple script to run coverage tests and generate reports
"""

import subprocess
import sys
import os
from datetime import datetime

def run_coverage():
    """Run coverage test and generate reports"""
    print("🎯 Running Tutorbot Coverage Test")
    print("=" * 40)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run the comprehensive coverage test
    try:
        result = subprocess.run([
            sys.executable, 'comprehensive_coverage_test.py'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ Coverage test completed successfully!")
        else:
            print(f"\n❌ Coverage test failed with return code: {result.returncode}")
            
    except Exception as e:
        print(f"❌ Error running coverage test: {e}")

def run_simple_coverage():
    """Run simple coverage using coverage.py directly"""
    print("🎯 Running Simple Coverage Test")
    print("=" * 40)
    
    try:
        # Start coverage
        result = subprocess.run([
            sys.executable, '-m', 'coverage', 'run', '--source=.', 'main.py'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        # Generate report
        report_result = subprocess.run([
            sys.executable, '-m', 'coverage', 'report'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        print("Coverage Report:")
        print(report_result.stdout)
        
        # Generate HTML report
        html_result = subprocess.run([
            sys.executable, '-m', 'coverage', 'html'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        print("✅ HTML report generated in htmlcov/ directory")
        
    except Exception as e:
        print(f"❌ Error running simple coverage: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "simple":
        run_simple_coverage()
    else:
        run_coverage()

