#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests",
# ]
# ///
"""
sonar-issues - Fetch code quality issues from SonarQube/SonarCloud

Usage: uv run sonar-issues.py <project-key> [options]

Options:
  --severities BLOCKER,CRITICAL,MAJOR,MINOR,INFO  Filter by severity (comma-separated)
  --types BUG,VULNERABILITY,CODE_SMELL            Filter by issue type (comma-separated)
  --statuses OPEN,CONFIRMED,REOPENED              Filter by status (comma-separated)
  --branch BRANCH_NAME                            Branch to check (default: current git branch)
  --check-env                                     Only check environment variables, don't fetch issues

Required environment variables:
  SONAR_TOKEN - Authentication token for SonarQube API
  SONAR_URL   - Base URL of your SonarQube instance (e.g., https://sonarcloud.io)

Examples:
  uv run sonar-issues.py my-project
  uv run sonar-issues.py my-project --severities BLOCKER,CRITICAL
  uv run sonar-issues.py my-project --branch feature/my-branch
  uv run sonar-issues.py --check-env
"""

import argparse
import json
import os
import subprocess
import sys
from urllib.parse import quote

import requests


# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    GREEN = '\033[0;32m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color

    @classmethod
    def enabled(cls) -> bool:
        """Check if colors should be enabled (stdout is a TTY)."""
        return sys.stdout.isatty()

    @classmethod
    def red(cls, text: str) -> str:
        return f"{cls.RED}{text}{cls.NC}" if cls.enabled() else text

    @classmethod
    def yellow(cls, text: str) -> str:
        return f"{cls.YELLOW}{text}{cls.NC}" if cls.enabled() else text

    @classmethod
    def green(cls, text: str) -> str:
        return f"{cls.GREEN}{text}{cls.NC}" if cls.enabled() else text

    @classmethod
    def bold(cls, text: str) -> str:
        return f"{cls.BOLD}{text}{cls.NC}" if cls.enabled() else text


def error(message: str) -> None:
    """Print error message and exit."""
    print(Colors.red(f"Error: {message}"), file=sys.stderr)
    sys.exit(1)


def warn(message: str) -> None:
    """Print warning message."""
    print(Colors.yellow(f"Warning: {message}"), file=sys.stderr)


def success(message: str) -> None:
    """Print success message."""
    print(Colors.green(message))


def check_env() -> bool:
    """Check that required environment variables are set.

    Returns True if all required variables are set, False otherwise.
    """
    missing = False

    if not os.environ.get('SONAR_TOKEN'):
        print(Colors.red("Error: SONAR_TOKEN environment variable is not set"), file=sys.stderr)
        print("", file=sys.stderr)
        print("To set SONAR_TOKEN:", file=sys.stderr)
        print("  1. Go to your SonarQube instance → My Account → Security → Generate Token", file=sys.stderr)
        print("  2. For SonarCloud: https://sonarcloud.io/account/security", file=sys.stderr)
        print("  3. Set the environment variable:", file=sys.stderr)
        print("     export SONAR_TOKEN='your-token-here'", file=sys.stderr)
        print("", file=sys.stderr)
        print("  Or add to your shell profile (~/.zshrc or ~/.bashrc):", file=sys.stderr)
        print("     export SONAR_TOKEN='your-token-here'", file=sys.stderr)
        print("", file=sys.stderr)
        missing = True

    if not os.environ.get('SONAR_URL'):
        print(Colors.red("Error: SONAR_URL environment variable is not set"), file=sys.stderr)
        print("", file=sys.stderr)
        print("To set SONAR_URL:", file=sys.stderr)
        print("  For SonarCloud:", file=sys.stderr)
        print("     export SONAR_URL='https://sonarcloud.io'", file=sys.stderr)
        print("", file=sys.stderr)
        print("  For self-hosted SonarQube:", file=sys.stderr)
        print("     export SONAR_URL='https://your-sonar-instance.com'", file=sys.stderr)
        print("", file=sys.stderr)
        print("  Add to your shell profile (~/.zshrc or ~/.bashrc) for persistence.", file=sys.stderr)
        print("", file=sys.stderr)
        missing = True

    return not missing


def get_current_git_branch() -> str | None:
    """Get the current git branch name.

    Returns the branch name, or None if:
    - Not in a git repository
    - In a detached HEAD state
    - Git command fails
    """
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            return None

        branch = result.stdout.strip()

        # Handle detached HEAD state
        if branch == 'HEAD':
            return None

        return branch
    except (subprocess.SubprocessError, FileNotFoundError):
        return None


def fetch_issues(
    project_key: str,
    branch: str | None = None,
    severities: str | None = None,
    types: str | None = None,
    statuses: str | None = None
) -> dict:
    """Fetch issues from SonarQube API.

    Returns the parsed JSON response.
    Raises SystemExit on error.
    """
    sonar_url = os.environ.get('SONAR_URL', '').rstrip('/')
    sonar_token = os.environ.get('SONAR_TOKEN', '')

    # Build API URL
    api_url = f"{sonar_url}/api/issues/search"
    params = {
        'componentKeys': project_key,
        'resolved': 'false',
        'ps': '500',  # Max page size
    }

    # Add branch parameter if specified
    if branch:
        params['branch'] = branch

    # Add optional filters
    if severities:
        params['severities'] = severities
    if types:
        params['types'] = types
    if statuses:
        params['statuses'] = statuses
    else:
        params['statuses'] = 'OPEN,CONFIRMED,REOPENED'

    # Make API request with basic auth (token as username, empty password)
    try:
        response = requests.get(
            api_url,
            params=params,
            auth=(sonar_token, ''),
            timeout=30
        )
    except requests.RequestException as e:
        error(f"Failed to connect to SonarQube API: {e}")

    # Handle HTTP errors
    if response.status_code == 401:
        error(
            f"Authentication failed. Your SONAR_TOKEN may be invalid or expired.\n\n"
            f"To generate a new token:\n"
            f"  1. Go to {sonar_url}/account/security\n"
            f"  2. Generate a new token\n"
            f"  3. Update your SONAR_TOKEN environment variable"
        )
    elif response.status_code == 403:
        error(f"Access forbidden. Your token may not have permission to access project '{project_key}'.")
    elif response.status_code == 404:
        error(
            f"Project '{project_key}' not found. Verify the project key is correct.\n\n"
            f"You can find your project key in SonarQube:\n"
            f"  1. Go to your project\n"
            f"  2. Look at the URL or project settings"
        )
    elif response.status_code != 200:
        error(f"API request failed with HTTP {response.status_code}.\n\nResponse: {response.text}")

    # Parse JSON response
    try:
        return response.json()
    except json.JSONDecodeError:
        error(f"Invalid JSON response from SonarQube API.\n\nResponse: {response.text}")


def format_issues(data: dict, project_key: str, branch: str | None) -> None:
    """Format and print issues from API response."""
    total = data.get('total', 0)
    issues = data.get('issues', [])

    if total == 0:
        branch_info = f" on branch '{branch}'" if branch else ""
        success(f"No issues found in project '{project_key}'{branch_info}!")
        return

    branch_info = f" on branch '{branch}'" if branch else ""
    print(f"Found {total} issue(s) in project '{project_key}'{branch_info}:")
    print()

    # Format each issue
    for issue in issues:
        key = issue.get('key', 'N/A')
        severity = issue.get('severity', 'N/A')
        issue_type = issue.get('type', 'N/A')
        rule = issue.get('rule', 'N/A')
        message = issue.get('message', 'N/A')
        component = issue.get('component', '')
        # Extract filename from component (format: project:path/to/file.ext)
        file_path = component.split(':')[-1] if ':' in component else component
        line = issue.get('line', 'N/A')
        status = issue.get('status', 'N/A')
        effort = issue.get('effort', 'N/A')

        print(f"## Issue: {key}")
        print(f"**Severity:** {severity}")
        print(f"**Type:** {issue_type}")
        print(f"**Rule:** {rule}")
        print(f"**Message:** {message}")
        print(f"**File:** {file_path}")
        print(f"**Line:** {line}")
        print(f"**Status:** {status}")
        print(f"**Effort:** {effort}")
        print()
        print("---")
        print()

    # Summary statistics
    print()
    print("=== Summary ===")

    # Group by severity
    severity_counts: dict[str, int] = {}
    for issue in issues:
        sev = issue.get('severity', 'UNKNOWN')
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    # Sort by priority order
    priority_order = ['BLOCKER', 'CRITICAL', 'MAJOR', 'MINOR', 'INFO']
    for sev in priority_order:
        if sev in severity_counts:
            print(f"  {sev}: {severity_counts[sev]}")

    # Print any unknown severities
    for sev, count in severity_counts.items():
        if sev not in priority_order:
            print(f"  {sev}: {count}")

    # Pagination warning
    if total > 500:
        warn(f"Showing first 500 of {total} issues. Run with more specific filters to see additional issues.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Fetch code quality issues from SonarQube/SonarCloud',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s my-project
  %(prog)s my-project --severities BLOCKER,CRITICAL
  %(prog)s my-project --branch feature/my-branch
  %(prog)s --check-env
'''
    )

    parser.add_argument(
        'project_key',
        nargs='?',
        help='SonarQube project key'
    )
    parser.add_argument(
        '--severities',
        help='Filter by severity (comma-separated): BLOCKER,CRITICAL,MAJOR,MINOR,INFO'
    )
    parser.add_argument(
        '--types',
        help='Filter by issue type (comma-separated): BUG,VULNERABILITY,CODE_SMELL'
    )
    parser.add_argument(
        '--statuses',
        help='Filter by status (comma-separated, default: OPEN,CONFIRMED,REOPENED)'
    )
    parser.add_argument(
        '--branch',
        help='Branch to check (default: auto-detect current git branch)'
    )
    parser.add_argument(
        '--check-env',
        action='store_true',
        help='Only check environment variables, don\'t fetch issues'
    )

    args = parser.parse_args()

    # Check environment variables
    env_ok = check_env()

    if not env_ok:
        sys.exit(1)

    # If only checking env, exit successfully
    if args.check_env:
        success("Environment variables are configured correctly.")
        print(f"SONAR_URL: {os.environ.get('SONAR_URL')}")
        sys.exit(0)

    # Validate project key
    if not args.project_key:
        error("Project key is required. Usage: sonar-issues.py <project-key> [options]")

    # Determine branch to use
    branch = args.branch
    if branch is None:
        # Auto-detect current git branch
        branch = get_current_git_branch()
        if branch:
            print(f"Auto-detected branch: {branch}")

    # Fetch issues
    data = fetch_issues(
        project_key=args.project_key,
        branch=branch,
        severities=args.severities,
        types=args.types,
        statuses=args.statuses
    )

    # Format and print issues
    format_issues(data, args.project_key, branch)


if __name__ == '__main__':
    main()
