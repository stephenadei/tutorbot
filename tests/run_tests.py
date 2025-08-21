#!/usr/bin/env python3
"""
Test runner for TutorBot comprehensive test suite
"""

import os
import sys
import unittest
import argparse
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import test configuration
from test_config import setup_test_environment, cleanup_test_environment, reset_test_data

def run_all_tests(verbosity=2):
    """Run all tests"""
    print("🧪 Running all TutorBot tests...")
    
    # Setup test environment
    setup_test_environment()
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Cleanup
    cleanup_test_environment()
    
    return result

def run_specific_test_category(category, verbosity=2):
    """Run tests for a specific category"""
    print(f"🧪 Running {category} tests...")
    
    # Setup test environment
    setup_test_environment()
    
    # Import the main test module
    import test_main as test_main
    
    # Map category names to test classes
    test_categories = {
        'translation': ['TestTranslation'],
        'message': ['TestMessageHandling'],
        'openai': ['TestOpenAIIntegration'],
        'prefill': ['TestPrefillFunctionality'],
        'segment': ['TestSegmentDetection'],
        'planning': ['TestPlanningFunctionality'],
        'payment': ['TestPaymentFunctionality'],
        'intake': ['TestIntakeFlow'],
        'menu': ['TestMenuHandling'],
        'webhook': ['TestWebhookHandling'],
        'utility': ['TestUtilityFunctions'],
        'email': ['TestEmailAndPaymentHandling'],
        'integration': ['TestIntegrationScenarios'],
        'error': ['TestErrorHandling'],
        'core': ['TestTranslation', 'TestMessageHandling', 'TestUtilityFunctions', 'TestMainImports'],
        'flow': ['TestIntakeFlow', 'TestMenuHandling', 'TestIntegrationScenarios'],
        'api': ['TestOpenAIIntegration', 'TestPaymentFunctionality', 'TestWebhookHandling', 'test_api_connection']
    }
    
    if category not in test_categories:
        print(f"❌ Unknown test category: {category}")
        print(f"Available categories: {', '.join(test_categories.keys())}")
        return None
    
    # Create test suite for the category
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for test_class_name in test_categories[category]:
        test_class = getattr(test_main, test_class_name, None)
        if test_class:
            tests = loader.loadTestsFromTestCase(test_class)
            suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Cleanup
    cleanup_test_environment()
    
    return result

def run_single_test(test_name, verbosity=2):
    """Run a single test method"""
    print(f"🧪 Running single test: {test_name}")
    
    # Setup test environment
    setup_test_environment()
    
    # Parse test name (format: TestClass.test_method)
    if '.' not in test_name:
        print("❌ Test name must be in format: TestClass.test_method")
        return None
    
    class_name, method_name = test_name.split('.', 1)
    
    # Import the main test module
    import test_main as test_main
    
    # Find the test class
    test_class = getattr(test_main, class_name, None)
    if not test_class:
        print(f"❌ Test class not found: {class_name}")
        return None
    
    # Create test suite with single test
    suite = unittest.TestSuite()
    suite.addTest(test_class(method_name))
    
    # Run test
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Cleanup
    cleanup_test_environment()
    
    return result

def print_test_summary(result):
    """Print detailed test summary"""
    print(f"\n{'='*80}")
    print(f"TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if result.failures:
        print(f"\n❌ FAILURES ({len(result.failures)}):")
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"{i}. {test}")
            print(f"   {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\n💥 ERRORS ({len(result.errors)}):")
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"{i}. {test}")
            print(f"   {traceback.split('Exception:')[-1].strip()}")
    
    if hasattr(result, 'skipped') and result.skipped:
        print(f"\n⏭️ SKIPPED ({len(result.skipped)}):")
        for i, (test, reason) in enumerate(result.skipped, 1):
            print(f"{i}. {test}: {reason}")
    
    print(f"\n{'='*80}")
    
    return len(result.failures) + len(result.errors)

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='Run TutorBot tests')
    parser.add_argument('--category', '-c', 
                       help='Run tests for specific category (translation, message, openai, etc.)')
    parser.add_argument('--test', '-t',
                       help='Run single test (format: TestClass.test_method)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--list-categories', '-l', action='store_true',
                       help='List available test categories')
    
    args = parser.parse_args()
    
    verbosity = 2 if args.verbose else 1
    
    # List categories if requested
    if args.list_categories:
        categories = [
            'translation', 'message', 'openai', 'prefill', 'segment',
            'planning', 'payment', 'intake', 'menu', 'webhook',
            'utility', 'email', 'integration', 'error',
            'core', 'flow', 'api'
        ]
        print("Available test categories:")
        for category in categories:
            print(f"  - {category}")
        return 0
    
    # Run tests based on arguments
    if args.test:
        result = run_single_test(args.test, verbosity)
    elif args.category:
        result = run_specific_test_category(args.category, verbosity)
    else:
        result = run_all_tests(verbosity)
    
    if result is None:
        return 1
    
    # Print summary and return exit code
    exit_code = print_test_summary(result)
    return exit_code

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 