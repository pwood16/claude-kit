# Feature: Migrate Sonar Plugin to uv and Current Branch Evaluation

## Feature Description
Update the `/sdlc:sonar` plugin to use Astral's `uv` tool for running the SonarQube issue fetcher instead of a bash script, and modify the default behavior to evaluate the current git branch's SonarQube compliance rather than always checking the main branch. This modernizes the script infrastructure and provides a more relevant developer experience by focusing on the branch being actively worked on.

## User Story
As a developer
I want the sonar command to check issues on my current working branch
So that I can fix code quality issues relevant to my active work without switching context to the main branch

## Problem Statement
The current sonar plugin implementation has two issues:
1. It uses a bash script (`sonar-issues`) which is harder to maintain and extend compared to Python
2. It queries SonarQube without specifying a branch, defaulting to the main branch, which means developers don't see issues specific to their feature branches

## Solution Statement
1. Rewrite the `sonar-issues` bash script as a Python script using PEP 723 inline dependencies, executed via `uv run`
2. Add automatic detection of the current git branch and pass it to the SonarQube API
3. Add an optional `--branch` flag to allow explicit branch specification when needed
4. Update the command file to invoke the Python script via `uv run`

## Relevant Files
Use these files to implement the feature:

- `plugins/sdlc/commands/sonar.md` - The command definition file that needs updating to use `uv run` instead of direct bash script execution
- `plugins/sdlc/scripts/sonar-issues` - The current bash script that will be replaced with a Python version
- `plugins/sdlc/README.md` - Documentation that needs updating to reflect the new uv dependency and branch behavior

### New Files
- `plugins/sdlc/scripts/sonar-issues.py` - New Python script with PEP 723 inline dependencies that replaces the bash script

## Implementation Plan

### Phase 1: Foundation
- Create the new Python script with PEP 723 inline dependencies for `requests` (HTTP client)
- Implement git branch detection using subprocess
- Ensure the script is fully self-contained with all dependencies declared inline

### Phase 2: Core Implementation
- Port all existing bash script functionality to Python:
  - Environment variable checking (`SONAR_TOKEN`, `SONAR_URL`)
  - Argument parsing (project key, severities, types, statuses, check-env)
  - SonarQube API calls
  - JSON parsing and formatting
  - Error handling
- Add the new `--branch` flag with auto-detection of current branch as default
- Implement colored output for terminal readability

### Phase 3: Integration
- Update `sonar.md` command to use `uv run` for script execution
- Remove the old bash script
- Update README.md with new uv requirement and branch behavior
- Test end-to-end

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create the new Python script with PEP 723 metadata
- Create `plugins/sdlc/scripts/sonar-issues.py`
- Add PEP 723 inline script metadata declaring dependencies:
  - `requests` for HTTP API calls
- Add `requires-python = ">=3.10"` for modern Python features
- Import required modules: `requests`, `subprocess`, `argparse`, `json`, `sys`, `os`

### Step 2: Implement environment variable checking
- Port the `check_env()` function from bash to Python
- Check for `SONAR_TOKEN` and `SONAR_URL` environment variables
- Print helpful setup instructions if either is missing
- Support `--check-env` flag to only validate environment

### Step 3: Implement argument parsing
- Use `argparse` to parse command-line arguments:
  - `project_key` (positional, required unless --check-env)
  - `--severities` (optional, comma-separated)
  - `--types` (optional, comma-separated)
  - `--statuses` (optional, comma-separated, default: OPEN,CONFIRMED,REOPENED)
  - `--branch` (optional, default: auto-detect current git branch)
  - `--check-env` (flag, check environment only)

### Step 4: Implement git branch auto-detection
- Use `subprocess.run()` to execute `git rev-parse --abbrev-ref HEAD`
- Handle the case where we're not in a git repository (fall back to no branch filter)
- Handle detached HEAD state gracefully
- Allow `--branch` flag to override auto-detection

### Step 5: Implement SonarQube API call
- Build the API URL: `${SONAR_URL}/api/issues/search`
- Add query parameters:
  - `componentKeys` (required)
  - `resolved=false` (always)
  - `branch` (from auto-detect or flag)
  - `severities` (if provided)
  - `types` (if provided)
  - `statuses` (default or provided)
  - `ps=500` (max page size)
- Use `requests.get()` with basic auth (token as username, empty password)
- Handle HTTP errors (401, 403, 404) with specific error messages

### Step 6: Implement issue formatting and output
- Parse JSON response
- Check if total issues is 0 and exit successfully with message
- Format each issue with severity, type, rule, message, file, line, status, effort
- Print summary statistics grouped by severity in priority order
- Handle pagination warning if more than 500 issues

### Step 7: Add colored terminal output
- Implement ANSI color codes for terminal output
- Use red for errors, yellow for warnings, green for success
- Detect if stdout is a TTY to disable colors when piped

### Step 8: Update sonar.md command file
- Change the allowed-tools to use `uv run` instead of direct script path:
  ```yaml
  allowed-tools:
    - Bash(uv run ${CLAUDE_PLUGIN_ROOT}/scripts/sonar-issues.py:*)
  ```
- Update the command instructions to document new `--branch` behavior
- Add note that uv must be installed

### Step 9: Update README.md
- Add uv as a prerequisite with installation instructions
- Document the new default branch behavior (auto-detects current branch)
- Document the `--branch` flag for explicit branch specification
- Update usage examples to show branch-related options

### Step 10: Remove old bash script
- Delete `plugins/sdlc/scripts/sonar-issues` (the bash version)

### Step 11: Make Python script executable
- Add shebang line: `#!/usr/bin/env python3`
- Set executable permission: `chmod +x plugins/sdlc/scripts/sonar-issues.py`

### Step 12: Run Validation Commands
- Execute all validation commands to ensure the feature works correctly with zero regressions

## Testing Strategy

### Unit Tests
- Test environment variable checking with missing `SONAR_TOKEN`
- Test environment variable checking with missing `SONAR_URL`
- Test git branch detection returns current branch name
- Test git branch detection handles non-git directories
- Test argument parsing with various flag combinations
- Test API URL construction includes branch parameter

### Edge Cases
- Not in a git repository (should work without branch filter or warn)
- Detached HEAD state (should use commit hash or skip branch)
- Branch name with special characters (should URL-encode)
- `--branch main` explicitly specified (should override auto-detect)
- SonarQube server doesn't support branch parameter (Community edition - should handle gracefully)
- uv not installed (should error with clear installation instructions)

## Acceptance Criteria
- [ ] Python script executes successfully via `uv run`
- [ ] Script auto-detects current git branch and passes to SonarQube API
- [ ] `--branch` flag overrides auto-detection
- [ ] All existing functionality preserved (env check, severities, types, etc.)
- [ ] Colored output works in terminal
- [ ] Error handling provides clear, actionable messages
- [ ] README.md documents uv prerequisite and branch behavior
- [ ] Old bash script is removed
- [ ] Command file updated to use `uv run`

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Verify uv is installed
uv --version

# Verify the new Python script exists and is executable
test -f plugins/sdlc/scripts/sonar-issues.py && echo "Python script exists"
test -x plugins/sdlc/scripts/sonar-issues.py && echo "Python script is executable"

# Verify the script has PEP 723 metadata
head -10 plugins/sdlc/scripts/sonar-issues.py | grep -q "# /// script" && echo "Has PEP 723 metadata"

# Verify the script has requests dependency declared
grep -q "requests" plugins/sdlc/scripts/sonar-issues.py && echo "Has requests dependency"

# Verify the old bash script is removed
test ! -f plugins/sdlc/scripts/sonar-issues && echo "Old bash script removed"

# Test environment variable check with uv (should show error for missing vars)
unset SONAR_TOKEN SONAR_URL
uv run plugins/sdlc/scripts/sonar-issues.py --check-env 2>&1 | grep -q "SONAR" && echo "Env check works"

# Test git branch detection (in a git repo)
cd plugins/sdlc && git rev-parse --abbrev-ref HEAD && cd ../..

# Verify command file uses uv run
grep -q "uv run" plugins/sdlc/commands/sonar.md && echo "Command uses uv run"

# Verify README mentions uv
grep -q "uv" plugins/sdlc/README.md && echo "README mentions uv"

# Verify README documents branch behavior
grep -qi "branch" plugins/sdlc/README.md && echo "README documents branch"

# Test script help output
uv run plugins/sdlc/scripts/sonar-issues.py --help

# Test plugin loads without errors (run from repo root)
claude --plugin-dir plugins/sdlc --help 2>&1 | head -5
```

## Notes
- Astral uv documentation: https://docs.astral.sh/uv/guides/scripts/
- PEP 723 defines the inline script metadata format
- SonarQube API branch parameter: `&branch=<branch-name>` in the issues search endpoint
- Branch analysis may require SonarQube Developer Edition or higher for full functionality
- Community Edition users may find the branch parameter still works in some versions
- The `requests` library is used instead of `urllib` for cleaner HTTP handling and better error messages
- Users without uv installed will see a clear error; uv installation is simple: `curl -LsSf https://astral.sh/uv/install.sh | sh`
