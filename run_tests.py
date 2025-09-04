#!/usr/bin/env python3
"""Test runner for Open Horizon AI system."""

import sys
import subprocess
import os
from pathlib import Path

def run_tests():
    """Run all tests for the Open Horizon AI system."""
    
    # Get the directory of this script
    test_dir = Path(__file__).parent / "tests"
    
    # Ensure we're in the right directory
    os.chdir(Path(__file__).parent)
    
    print("🧪 Running Open Horizon AI Test Suite")
    print("=" * 50)
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--color=yes",  # Colored output
        "-x",  # Stop on first failure (remove for full test run)
    ]
    
    # Add coverage if pytest-cov is available
    try:
        import pytest_cov
        cmd.extend([
            "--cov=.",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])
        print("📊 Coverage reporting enabled")
    except ImportError:
        print("ℹ️  pytest-cov not available, skipping coverage")
    
    print(f"🔍 Running command: {' '.join(cmd)}")
    print()
    
    # Run the tests
    try:
        result = subprocess.run(cmd, check=False)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
            print("📋 See VALIDATION_REPORT.md for detailed results")
            if "pytest_cov" in locals():
                print("📈 Coverage report available in htmlcov/index.html")
        else:
            print(f"\n❌ Tests failed with return code {result.returncode}")
            return False
            
    except KeyboardInterrupt:
        print("\n⏹️  Test run interrupted")
        return False
    except Exception as e:
        print(f"\n💥 Error running tests: {e}")
        return False
    
    return True

def run_specific_test_suite(suite_name):
    """Run a specific test suite."""
    
    valid_suites = {
        "agent": "test_agent.py",
        "tools": "test_tools.py", 
        "api": "test_api.py",
        "integration": "test_integration.py",
        "models": "test_models.py"
    }
    
    if suite_name not in valid_suites:
        print(f"❌ Invalid test suite: {suite_name}")
        print(f"Valid suites: {', '.join(valid_suites.keys())}")
        return False
    
    test_file = f"tests/{valid_suites[suite_name]}"
    
    print(f"🧪 Running {suite_name} test suite")
    print("=" * 50)
    
    cmd = [
        sys.executable, "-m", "pytest",
        test_file,
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except Exception as e:
        print(f"💥 Error running {suite_name} tests: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test suite
        suite = sys.argv[1]
        success = run_specific_test_suite(suite)
    else:
        # Run all tests
        success = run_tests()
    
    sys.exit(0 if success else 1)