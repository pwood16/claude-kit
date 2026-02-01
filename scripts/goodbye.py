#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
goodbye - A simple goodbye world function for demonstration and testing.

This module provides a minimal example of a Python utility function that prints
'Goodbye World' to stdout. It serves as a complement to the hello function and
demonstrates consistent implementation patterns in the claude-kit project.

Usage:
    python3 scripts/goodbye.py
    ./scripts/goodbye.py
    uv run --script scripts/goodbye.py
"""

import argparse


def goodbye() -> None:
    """Print 'Goodbye World' to stdout.

    This is a simple demonstration function that prints a farewell
    message, mirroring the hello function pattern.
    """
    print('Goodbye World')


def main() -> None:
    """Main entry point for the goodbye script."""
    parser = argparse.ArgumentParser(
        description="Print 'Goodbye World' to stdout",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.parse_args()
    goodbye()


if __name__ == "__main__":
    main()
