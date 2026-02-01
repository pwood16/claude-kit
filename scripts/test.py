#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
test - A simple test function for demonstration and validation.

This module provides a minimal example of a Python test utility that performs
basic assertions and validations. It demonstrates assertion patterns and serves
as a template for adding test utilities to the claude-kit project.

Usage:
    python3 scripts/test.py
    ./scripts/test.py
    uv run --script scripts/test.py
    python3 scripts/test.py --help
    python3 scripts/test.py --verbose
"""

import argparse


def test(verbose: bool = False) -> bool:
    """Run simple test assertions and print results.

    This function performs basic test assertions including arithmetic,
    string comparisons, boolean logic, and list operations. It tracks
    pass/fail status and prints results in a clear format.

    Args:
        verbose: If True, print detailed information for each test.

    Returns:
        True if all tests passed, False otherwise.
    """
    tests = [
        ("Arithmetic: 1 + 1 == 2", lambda: 1 + 1 == 2),
        ("String comparison: 'test' == 'test'", lambda: 'test' == 'test'),
        ("Boolean logic: True and True == True", lambda: True and True == True),
        ("List operations: [1, 2, 3] == [1, 2, 3]", lambda: [1, 2, 3] == [1, 2, 3]),
    ]

    passed = 0
    failed = 0

    print("Running tests...\n")

    for description, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                status = "✓ PASS"
            else:
                failed += 1
                status = "✗ FAIL"
        except Exception as e:
            failed += 1
            status = f"✗ ERROR: {e}"

        if verbose:
            print(f"{status}: {description}")

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*60}")

    if failed == 0:
        print("✓ All tests passed!")
        return True
    else:
        print(f"✗ {failed} test(s) failed")
        return False


def main() -> None:
    """Main entry point for the test script."""
    parser = argparse.ArgumentParser(
        description="Run simple test assertions and validations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output for each test"
    )
    args = parser.parse_args()

    all_passed = test(verbose=args.verbose)

    # Set exit code: 0 for success, 1 for failure
    import sys
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
