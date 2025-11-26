#!/usr/bin/env python3
"""
Test runner for CalcScript+ compiler
Runs all test programs and displays results
"""

import subprocess
import sys
from pathlib import Path


def run_test(test_file: Path, show_output: bool = True):
    """Run a single test file"""
    print("=" * 70)
    print(f"Running: {test_file.name}")
    print("=" * 70)
    
    try:
        # Get path to main.py
        main_py = Path(__file__).parent.parent.parent / '3_Implementation' / 'main.py'
        result = subprocess.run(
            [sys.executable, str(main_py), str(test_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("[PASS] Test passed")
            if show_output:
                print("\nOutput:")
                print(result.stdout)
        else:
            print("[FAIL] Test failed")
            print("\nError:")
            print(result.stderr)
        
        return result.returncode == 0
    
    except subprocess.TimeoutExpired:
        print("[FAIL] Test timed out")
        return False
    except Exception as e:
        print(f"[FAIL] Error running test: {e}")
        return False


def main():
    """Run all tests"""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    tests_dir = script_dir / 'tests'
    
    if not tests_dir.exists():
        print(f"Error: tests directory not found at {tests_dir}")
        sys.exit(1)
    
    # Find all .calc files
    test_files = sorted(tests_dir.glob('*.calc'))
    
    if not test_files:
        print("No test files found")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("CalcScript+ Compiler - Test Suite")
    print("=" * 70)
    print(f"\nFound {len(test_files)} test(s)\n")
    
    results = []
    for test_file in test_files:
        passed = run_test(test_file)
        results.append((test_file.name, passed))
        print()
    
    # Summary
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Total: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print(f"\n{total_count - passed_count} test(s) failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
