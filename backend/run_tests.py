#!/usr/bin/env python3
"""
Test runner for FitMe backend functionality.
"""

import os
import sys
import unittest
import subprocess


def run_backend_tests():
    """Run all backend tests and return results."""
    print("🧪 Running FitMe Backend Tests\n" + "="*50)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*50)
    print(f"📊 Test Summary:")
    print(f"   ✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   ❌ Failed: {len(result.failures)}")
    print(f"   💥 Errors: {len(result.errors)}")
    print(f"   📈 Total: {result.testsRun}")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   • {test}")
    
    if result.errors:
        print(f"\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   • {test}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    if success:
        print(f"\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  Some tests failed. See details above.")
    
    return success


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8+ required")
        return False
    return True


def check_dependencies():
    """Check if required dependencies are available."""
    required_modules = ['unittest', 'datetime', 'json', 'os', 'tempfile']
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        return False
    
    return True


def main():
    """Main test runner entry point."""
    print("🚀 FitMe Backend Test Suite")
    print("=" * 30)
    
    # Pre-flight checks
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    # Run tests
    success = run_backend_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()