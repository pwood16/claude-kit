# Feature: SDLC Feature Loop Script

## Feature Description
A Python script (using uv for dependency management) that chains together the SDLC feature planning, implementation, and review workflow into an automated loop. The script takes a feature prompt, creates a plan using `/sdlc:feature`, implements it using `/sdlc:implement`, then iteratively runs code review using the `acr` CLI tool and addresses any findings until the code receives a clean review (LGTM with no issues).

## User Story
As a developer
I want to run a single command that plans, implements, and iteratively reviews my feature
So that I can automate the full development lifecycle and ensure quality code with minimal manual intervention

## Problem Statement
Currently, using the SDLC plugin requires manually invoking separate commands (`/sdlc:feature`, `/sdlc:implement`) and then manually running code review tools. This creates friction in the development workflow and requires the developer to context-switch between planning, implementation, and review phases. There's no automated way to ensure code quality through iterative review until the code passes all checks.

## Solution Statement
Create a new Python script (`feature-loop`) that:
1. Takes a feature description as input
2. Calls Claude CLI with `/sdlc:feature` to create a plan
3. Calls Claude CLI with `/sdlc:implement` to implement the plan
4. Runs `acr` to review the code
5. If issues are found, calls Claude CLI to **triage** each finding:
   - If the finding is a **real issue**: fix the code
   - If the finding is a **false positive**: add an explanatory comment in the code at the location of the finding explaining why the current implementation is correct
6. Repeats steps 4-5 until `acr` returns no findings (exit code 0)
7. Logs progress to stdout at each step

The script will use `uv` inline script dependencies for Python package management and subprocess calls to invoke the Claude CLI and acr tools.

## Relevant Files
Use these files to implement the feature:

- `plugins/sdlc/README.md` - Documents the existing SDLC commands, will need to be updated to include the new script
- `plugins/sdlc/commands/feature.md` - The feature planning command template that will be invoked
- `plugins/sdlc/commands/implement.md` - The implementation command template that will be invoked
- `plugins/sdlc/.claude-plugin/plugin.json` - Plugin manifest, may need updating
- `plugins/spawn/scripts/ralph-loop` - Reference implementation showing how to run Claude in a loop with completion detection

### New Files
- `plugins/sdlc/scripts/feature-loop` - The main Python script that orchestrates the feature development loop
- `plugins/sdlc/commands/review.md` - New review command that wraps acr for single-use review (optional, for standalone use)

## Implementation Plan
### Phase 1: Foundation
- Create the `scripts/` directory under the sdlc plugin
- Create the basic Python script structure with uv inline dependencies
- Implement logging utilities for consistent stdout output at each step
- Implement subprocess helper functions for running Claude CLI and acr

### Phase 2: Core Implementation
- Implement the feature planning step (invoke `claude -p` with feature prompt)
- Implement the implementation step (invoke `claude -p` with implement prompt and plan file path)
- Implement the review loop using `acr` CLI
- Implement the fix iteration logic when issues are found
- Add argument parsing for feature prompt input and configuration options

### Phase 3: Integration
- Make the script executable
- Update the plugin README with documentation
- Test the full workflow end-to-end

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create the scripts directory structure
- Create `plugins/sdlc/scripts/` directory if it doesn't exist
- This follows the pattern established by `plugins/spawn/scripts/`

### Step 2: Create the feature-loop Python script with uv dependencies
- Create `plugins/sdlc/scripts/feature-loop` with:
  - Shebang line: `#!/usr/bin/env -S uv run --script`
  - Inline script dependencies block for any needed packages
  - Main script structure with argument parsing using argparse
  - Logging helper function that prefixes output with step indicators
  - Constants for paths and configuration

### Step 3: Implement the feature planning function
- Function: `run_feature_plan(feature_prompt: str) -> str`
- Constructs the Claude CLI command to invoke `/sdlc:feature` with the feature prompt
- Runs: `claude --dangerously-skip-permissions -p "/sdlc:feature {prompt}"`
- Parses output to extract the plan file path (specs/issue-*.md)
- Logs each step to stdout
- Returns the path to the created plan file

### Step 4: Implement the implementation function
- Function: `run_implement(plan_path: str) -> None`
- Constructs the Claude CLI command to invoke `/sdlc:implement` with the plan file
- Runs: `claude --dangerously-skip-permissions -p "/sdlc:implement {plan_path}"`
- Logs progress to stdout

### Step 5: Implement the code review function
- Function: `run_review() -> tuple[int, str]`
- Runs: `acr --local` to perform code review without posting to PR
- Captures exit code and output
- Exit code 0 = no findings (LGTM)
- Exit code 1 = findings found
- Exit code 2 = error
- Logs review results to stdout
- Returns (exit_code, output)

### Step 6: Implement the triage and fix issues function
- Function: `triage_and_fix_issues(review_output: str) -> None`
- Constructs a Claude CLI prompt with the review findings that instructs the agent to:
  1. Analyze each finding to determine if it's a real issue or a false positive
  2. For **real issues**: Fix the code to address the concern
  3. For **false positives**: Add an explanatory comment at the location of the finding (e.g., `# NOTE: <explanation of why this is intentional and correct>`)
- The prompt should emphasize that the agent must make a judgment call on each finding
- Runs: `claude --dangerously-skip-permissions -p "<triage prompt with findings>"`
- Logs the triage decision (fix vs false positive) for each finding to stdout
- Logs progress to stdout

### Step 7: Implement the main orchestration loop
- Parse command line arguments (feature prompt, max iterations, verbose flag)
- Log start of feature loop with configuration
- Step 1: Call `run_feature_plan()` and log the plan file created
- Step 2: Call `run_implement()` and log completion
- Step 3: Enter review loop:
  - Call `run_review()`
  - If exit code 0: log LGTM and break
  - If exit code 1: log findings count, call `triage_and_fix_issues()`, continue loop
  - If exit code 2: log error and exit with error code
  - Check iteration count against max (default: 5)
- Log final status (success or max iterations reached)

### Step 8: Add command line argument handling
- `--prompt` or positional argument: The feature description (required)
- `--max-review-iterations`: Maximum review/fix cycles (default: 5)
- `--verbose` or `-v`: Enable verbose logging
- `--skip-review`: Skip the review loop (just plan and implement)

### Step 9: Make the script executable and test
- Add execute permission to the script
- Test running `./feature-loop --help` to verify argument parsing
- Run the validation commands

### Step 10: Update plugin documentation
- Update `plugins/sdlc/README.md` to document the new `feature-loop` script
- Add usage examples and description of the workflow

### Step 11: Run validation commands
- Run all validation commands listed below to ensure the feature works correctly

## Testing Strategy
### Unit Tests
- Test argument parsing with various input combinations
- Test log output format consistency
- Test plan file path extraction from Claude output

### Edge Cases
- Empty feature prompt (should show error)
- Claude CLI not available in PATH
- acr not available in PATH
- Max iterations reached without clean review
- Network/API errors during Claude invocation
- Plan file not created (parsing failure)
- Review loop with persistent issues
- All findings are false positives (should add comments and pass next review)
- Mix of real issues and false positives in same review
- Same false positive flagged repeatedly (comment should prevent re-flagging)

## Acceptance Criteria
- Script can be invoked with `./feature-loop "feature description"`
- Script logs each step clearly to stdout with timestamps
- Script successfully creates a plan file in `specs/` directory
- Script successfully implements the plan
- Script runs acr for code review and captures results
- Script triages each finding as either a real issue or false positive
- For real issues: script fixes the code
- For false positives: script adds explanatory comments at the finding location
- Script iteratively reviews until acr returns clean (exit 0)
- Script respects --max-review-iterations flag
- Script exits gracefully on errors with informative messages
- Script is documented in the plugin README

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Verify the script exists and is executable
ls -la plugins/sdlc/scripts/feature-loop

# Verify the script has correct shebang and can show help
plugins/sdlc/scripts/feature-loop --help

# Verify uv can parse the script dependencies
uv run --script plugins/sdlc/scripts/feature-loop --help

# Verify syntax is valid Python
python3 -m py_compile plugins/sdlc/scripts/feature-loop

# Dry run test - verify the script structure (will fail at Claude call, but validates parsing)
# This tests that imports and argument parsing work
plugins/sdlc/scripts/feature-loop --help 2>&1 | grep -q "usage\|positional\|optional" && echo "Help output OK"
```

## Notes
- The script follows the pattern established by `plugins/spawn/scripts/ralph-loop` but uses Python instead of zsh for better error handling and maintainability
- Using `uv run --script` allows inline dependency specification without needing a separate requirements.txt
- The `--dangerously-skip-permissions` flag is used for Claude CLI to enable autonomous operation
- The `acr --local` flag ensures reviews don't post to GitHub PRs
- **False positive handling**: The triage step is critical because `acr` can report false positives. The agent must use judgment to determine if each finding is valid. Adding explanatory comments for false positives serves two purposes: (1) documents the reasoning for future developers, and (2) may help `acr` avoid re-flagging the same location in subsequent reviews
- Consider adding `--dry-run` flag in future iterations to preview commands without execution
- Future enhancement: Add support for passing custom prompts to the review fix step
- Future enhancement: Add git commit between iterations (like ralph-loop does)
