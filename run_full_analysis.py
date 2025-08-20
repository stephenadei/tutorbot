#!/usr/bin/env python3
"""
Full Code Analysis for Tutorbot
Runs comprehensive analysis and generates complete report
"""

import subprocess
import sys
import os
from datetime import datetime

def run_analysis():
    """Run full code analysis"""
    print("🎯 Tutorbot Full Code Analysis")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Run simple code analysis
    print("📊 Step 1: Running code structure analysis...")
    try:
        result = subprocess.run([
            sys.executable, 'simple_code_analysis.py'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        print("Code Analysis Results:")
        print(result.stdout)
        
        if result.stderr:
            print("Warnings/Errors:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error running code analysis: {e}")
    
    print("\n" + "="*50)
    
    # Step 2: Run coverage test
    print("📈 Step 2: Running coverage test...")
    try:
        result = subprocess.run([
            sys.executable, 'run_coverage.py', 'simple'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        print("Coverage Test Results:")
        print(result.stdout)
        
        if result.stderr:
            print("Warnings/Errors:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error running coverage test: {e}")
    
    print("\n" + "="*50)
    
    # Step 3: Show coverage summary
    print("📋 Step 3: Coverage summary...")
    try:
        result = subprocess.run([
            sys.executable, 'view_coverage_report.py'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        # Extract summary from output
        lines = result.stdout.split('\n')
        summary_lines = []
        in_summary = False
        
        for line in lines:
            if '📊 Coverage Summary:' in line:
                in_summary = True
            elif in_summary and line.startswith('🌐 Options:'):
                break
            elif in_summary:
                summary_lines.append(line)
        
        print('\n'.join(summary_lines))
        
    except Exception as e:
        print(f"❌ Error showing coverage summary: {e}")
    
    print("\n" + "="*50)
    
    # Step 4: Generate final recommendations
    print("💡 Step 4: Final recommendations...")
    generate_recommendations()

def generate_recommendations():
    """Generate final recommendations based on analysis"""
    print("\n🎯 CRITICAL RECOMMENDATIONS:")
    print("=" * 40)
    
    print("\n🚨 IMMEDIATE ACTIONS REQUIRED:")
    print("1. BREAK DOWN main.py (6,204 lines) - This is a major code smell!")
    print("   - Split into multiple modules")
    print("   - Target: Reduce to <500 lines")
    
    print("\n2. REFACTOR MASSIVE FUNCTIONS:")
    print("   - t() function: 1,040 lines (split into translation modules)")
    print("   - handle_message_created(): 494 lines (split by message type)")
    print("   - handle_intake_step(): 297 lines (split by step)")
    
    print("\n3. IMPROVE TEST COVERAGE:")
    print("   - Current coverage is very low")
    print("   - Start with utility functions")
    print("   - Target: 50%+ coverage")
    
    print("\n📋 REFACTORING PLAN:")
    print("Week 1: Create module structure")
    print("Week 2: Move utility functions")
    print("Week 3: Break down large functions")
    print("Week 4: Add comprehensive tests")
    
    print("\n📁 SUGGESTED MODULE STRUCTURE:")
    print("├── main.py (entry point)")
    print("├── handlers/")
    print("│   ├── message_handler.py")
    print("│   ├── menu_handler.py")
    print("│   └── flow_handler.py")
    print("├── services/")
    print("│   ├── translation_service.py")
    print("│   ├── chatwoot_service.py")
    print("│   └── payment_service.py")
    print("├── utils/")
    print("│   ├── helpers.py")
    print("│   └── validators.py")
    print("└── models/")
    print("    ├── conversation.py")
    print("    └── contact.py")
    
    print("\n✅ SUCCESS METRICS:")
    print("- main.py < 500 lines")
    print("- No functions > 50 lines")
    print("- 50%+ test coverage")
    print("- Improved maintainability")

def main():
    """Main function"""
    run_analysis()
    
    print(f"\n✅ Full analysis completed!")
    print(f"📁 Check the following files:")
    print(f"   - coverage_summary_report.md (Detailed report)")
    print(f"   - coverage_html/ (HTML coverage report)")
    print(f"   - .coverage (Coverage data)")
    
    print(f"\n🎯 Next steps:")
    print(f"   1. Review the analysis results")
    print(f"   2. Start with breaking down main.py")
    print(f"   3. Focus on the largest functions first")
    print(f"   4. Add unit tests as you refactor")

if __name__ == "__main__":
    main()
