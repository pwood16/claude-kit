#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
hello - A simple hello world function for demonstration and testing.

This module provides a minimal example of a Python utility function that prints
'Hello World' to stdout. It serves as a template for adding other simple utilities
to the claude-kit project.

Usage:
    python3 scripts/hello.py
    ./scripts/hello.py
    uv run --script scripts/hello.py
"""

import argparse


def hello() -> None:
    """Print 'Hello World' to stdout.

    This is a simple demonstration function that prints the classic
    'Hello World' greeting message.
    """
    print('Hello World')


def main() -> None:
    """Main entry point for the hello script."""
    parser = argparse.ArgumentParser(
        description="Print 'Hello World' to stdout",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.parse_args()
    hello()


if __name__ == "__main__":
    main()
