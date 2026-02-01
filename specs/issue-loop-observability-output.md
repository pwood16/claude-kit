# Feature: Loop Observability with Iteration Output

## Feature Description
Enhance the ralph-loop and feature-loop workflows with comprehensive observability by outputting detailed, structured summaries after each iteration. Users will see clear summaries of task completions, file modifications, ACR review findings, and overall progress at each step. This transforms the current verbose stream of output into digestible progress reports that make it easy to understand what's happening during long-running automated workflows.

## User Story
As a developer using feature-loop and ralph-loop
I want to see clear, structured summaries of what each iteration accomplished
So that I can monitor progress at a glance, quickly identify issues, and have confidence in the automated workflow without parsing through verbose logs.

## Problem Statement
Currently, ralph-loop and feature-loop run iterations back-to-back with continuous verbose output but lack clear iteration boundaries and summaries. Users experience:

1. **No iteration summaries in ralph-loop**: Output streams by without showing which task was completed, what files changed, or iteration status
2. **No ACR findings summaries in feature-loop**: Review results aren't summarized before triage, making it hard to understand what issues were found
3. **Poor progress visibility**: No clear indication of overall progress (tasks completed vs remaining)
4. **Difficult debugging**: When issues occur, it's hard to identify which iteration caused them
5. **No historical tracking**: Progress logs lack structured summaries for post-mortem analysis

This makes monitoring long-running workflows difficult and reduces confidence in the automation.

## Solution Statement
Add structured iteration summaries to both scripts:

**Ralph-loop enhancements:**
- After each iteration, display a formatted summary showing:
  - Iteration number and timestamp
  - Task that was targeted (h3 heading for Markdown, story title for JSON)
  - Task completion status (complete/incomplete)
  - Files modified, added, or deleted during iteration
  - Exit code and any errors
  - Overall progress (X of Y tasks complete)
- Write summaries to progress log for historical reference
- Use color coding for quick visual scanning (green=success, yellow=warning, red=error)
- Add visual separators (lines of dashes/equals) between iterations

**Feature-loop enhancements:**
- After ralph-loop completes, display summary of implementation phase:
  - Total iterations run
  - Total tasks completed
  - Files modified during implementation
- After each ACR review run, display findings summary before triage:
  - Total findings count
  - Breakdown by severity (if available)
  - Files with issues (with count per file)
  - Brief overview of finding types
  - LGTM status or indication that fixes are needed
- Save all summaries to progress logs

**Additional features:**
- `--summary-only` flag: Show only summaries, suppress verbose Claude output
- `--no-summaries` flag: Disable summaries for backwards compatibility
- ANSI color detection: Auto-disable colors when piping output

## Relevant Files
Use these files to implement the feature:

### Existing Files

**plugins/spawn/scripts/ralph-loop** (Python script, 559 lines)
- Main loop logic that runs Claude iterations
- Lines 471-531: Main iteration loop - needs summary output after each iteration
- Lines 397-426: `commit_changes()` function - can be extended to capture git diff
- Lines 172-189: `initialize_progress_file()` - progress file initialization
- Lines 216-254: `check_markdown_completion()` - can be enhanced to extract task titles
- Lines 192-214: `check_json_completion()` - can be enhanced to extract story titles
- Lines 356-395: `run_claude_iteration()` - captures output that can be analyzed
- Needs: formatting utilities, git diff capture, summary generation, summary output

**plugins/sdlc/scripts/feature-loop** (Python script, 882 lines)
- Orchestrates planning, implementation, and review phases
- Lines 443-468: `run_implement()` - calls ralph-loop, needs to parse and display summary afterward
- Lines 470-504: `run_review()` - runs ACR review, returns output
- Lines 830-864: Review loop - needs to display ACR summary before calling triage
- Lines 506-560: `triage_and_fix_issues()` - receives review output
- Needs: ACR output parsing, summary formatting, ralph-loop output parsing

### New Files
None required - all changes are enhancements to existing scripts.

## Implementation Plan

### Phase 1: Foundation
Create utility functions in both scripts for formatting output with visual separators, color codes, and structured data presentation. Add git diff capture capabilities to ralph-loop to track file changes per iteration.

### Phase 2: Core Implementation
Implement summary generation in ralph-loop to capture task status, file changes, and iteration results. Parse and format this information into concise, readable summaries that appear after each iteration. Enhance feature-loop to parse ralph-loop output and ACR findings, generating summaries at appropriate checkpoints.

### Phase 3: Integration
Wire up all summaries to appear at the right moments: after each ralph-loop iteration, after the implementation phase completes, and after each ACR review run. Ensure all summaries are logged to progress files with timestamps. Add command-line flags for controlling summary verbosity and update documentation.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add output formatting utilities to ralph-loop
**Status:** complete
- Add a `format_separator()` function to create visual dividers (lines of = or -)
- Add `supports_color()` function to detect if terminal supports ANSI colors
- Add color code constants (GREEN, YELLOW, RED, BLUE, RESET) that respect color support
- Add `format_iteration_summary()` function skeleton that takes structured data and returns formatted text
- Add timestamp formatting helper `format_timestamp()` for consistent time display

### Step 2: Add git change tracking to ralph-loop
**Status:** complete
- Add `get_git_status()` function that runs `git status --porcelain` and parses output into added/modified/deleted lists
- In the main loop, before running Claude iteration (line ~508), capture git status as `before_files`
- After iteration completes (line ~510), capture git status as `after_files`
- Add `diff_file_changes()` function to compute the delta between before/after (newly added, modified, deleted)
- Store this information in a data structure for summary generation

### Step 3: Add task extraction utilities to ralph-loop
**Status:** complete
- Enhance `check_markdown_completion()` to return not just count, but also list of (title, status) tuples
- Add `get_markdown_tasks()` function that returns all task titles and statuses from spec
- Enhance `check_json_completion()` to return list of (story_id, title, status) tuples
- Add `get_json_stories()` function that returns all story details from spec
- Add `find_current_task()` function that identifies which task/story is currently incomplete

### Step 4: Implement iteration summary generation in ralph-loop
**Status:** complete
- Add `generate_iteration_summary()` function that takes:
  - Iteration number
  - Spec format (markdown/json)
  - Spec file path
  - File changes (added, modified, deleted lists)
  - Exit code
  - Current task info
- Function should return a formatted string with:
  - Visual separator line (===)
  - Header: "Iteration N Summary - [timestamp]"
  - Task worked on (title)
  - Task status (complete/incomplete, color-coded)
  - Files changed (grouped by added/modified/deleted)
  - Exit status (success/failed, color-coded)
  - Progress: "X of Y tasks complete"
  - Visual separator line (===)

### Step 5: Display iteration summaries in ralph-loop main loop
**Status:** complete
- After iteration completes and changes are committed (line ~527), call `generate_iteration_summary()`
- Print the formatted summary to stdout
- Append the summary to progress file with a clear section header
- Add a blank line after summary for readability
- Test with both Markdown and JSON spec formats

### Step 6: Add ACR output parsing utilities to feature-loop
**Status:** complete
- Add `parse_acr_output()` function that extracts:
  - Total findings count
  - List of files with issues (use regex to find file paths in output)
  - Count of findings per file
  - Extract finding types/categories if present in output
  - LGTM status (exit code 0) or issues found status
- Function should return a structured dictionary with parsed data
- Handle edge cases: empty output, malformed output, zero findings

### Step 7: Add ACR summary formatting to feature-loop
**Status:** complete
- Add `format_acr_summary()` function that takes parsed ACR data and returns formatted string:
  - Visual separator line (===)
  - Header: "Code Review Summary - Iteration N - [timestamp]"
  - Total findings count (color-coded: green if 0, yellow/red if >0)
  - List of affected files with finding count per file
  - Brief overview of finding categories (if available)
  - Status: "LGTM ✓" or "Issues found - proceeding to triage"
  - Visual separator line (===)
- Add color support utilities similar to ralph-loop

### Step 8: Display ACR summaries in feature-loop review loop
**Status:** complete
- In the review loop (lines 830-864), after `run_review()` returns (line ~833):
  - Parse the review output with `parse_acr_output()`
  - Generate summary with `format_acr_summary()`
  - Print the summary to stdout
  - If exit code is 0 (LGTM), the summary shows success
  - If exit code is 1 (findings), the summary shows issues before calling triage

### Step 9: Add ralph-loop completion summary to feature-loop
**Status:** complete
- After `run_implement()` completes (line ~807), parse the implementation results:
  - Read the progress file to count how many iterations were run
  - Use spec file to determine total tasks and completed tasks
  - Find files modified during implementation (compare git state before/after)
- Add `format_implementation_summary()` function that displays:
  - Visual separator line (===)
  - Header: "Implementation Phase Complete - [timestamp]"
  - Total iterations: N
  - Tasks completed: X of Y
  - Files modified during implementation (list)
  - Status: "Ready for review" or "Some tasks incomplete"
  - Visual separator line (===)
- Print this summary before moving to review phase

### Step 10: Add command-line flags for summary control
**Status:** complete
- Add `--summary-only` flag to ralph-loop:
  - When enabled, suppress verbose Claude output (redirect stdout of subprocess to /dev/null or capture without printing)
  - Still show summaries after each iteration
  - Update help text
- Add `--no-summaries` flag to ralph-loop:
  - When enabled, skip generating and displaying summaries
  - For backwards compatibility or when user wants raw output only
  - Update help text
- Update argparse configuration in both scripts

### Step 11: Update progress file logging
**Status:** complete
- Ensure all iteration summaries in ralph-loop are written to progress file with timestamps
- Use clear section headers like `=== Iteration N Summary ===`
- Ensure ACR summaries in feature-loop could be logged (add optional logging)
- Keep format human-readable and grep-friendly (plain text, no color codes in files)
- Add implementation summary to progress or checkpoint file

### Step 12: Update documentation
- Update `plugins/spawn/README.md`:
  - Add section describing new summary output format
  - Document `--summary-only` and `--no-summaries` flags
  - Add example of what a summary looks like (text example)
  - Update "Ralph mode" section to mention iteration summaries
- Update `plugins/sdlc/README.md`:
  - Add section describing enhanced observability features
  - Explain implementation summary and ACR summary formats
  - Mention that summaries appear automatically during feature-loop
- Add examples showing the summary output format in both files

### Step 13: Test with a real spec file
- Create a test Markdown spec with 3 simple tasks:
  - Step 1: Create a test file with some content
  - Step 2: Modify the test file
  - Step 3: Delete the test file
- Run ralph-loop with `--spec` pointing to test spec
- Verify summaries appear after each iteration
- Verify summaries show correct task titles, file changes, and progress
- Verify progress file contains all summaries with timestamps
- Test `--summary-only` and `--no-summaries` flags

### Step 14: Test feature-loop integration
- Run feature-loop with a simple feature (use `--max-implement-iterations 3` and `--max-review-iterations 2` to limit)
- Verify implementation summary appears after ralph-loop completes
- Verify ACR summaries appear after each review run (if not using `--skip-review`)
- Check that summaries are clear and informative
- Verify no regressions in existing functionality (checkpoint saving, resume, etc.)

### Step 15: Run validation commands
- Execute all commands in the Validation Commands section below
- Verify all tests pass with zero errors
- Verify summary output appears correctly in all scenarios
- Verify progress files are correctly formatted
- Confirm no regressions in core loop functionality

## Testing Strategy

### Unit Tests
- Test `format_separator()` with different widths and characters
- Test `supports_color()` with various TERM values and output redirects
- Test `get_git_status()` with different git states (clean, modified, untracked, deleted files)
- Test `diff_file_changes()` with before/after lists
- Test `get_markdown_tasks()` and `get_json_stories()` with sample specs
- Test `find_current_task()` with various completion states
- Test `generate_iteration_summary()` with different inputs
- Test `parse_acr_output()` with sample ACR output (LGTM and findings)
- Test `format_acr_summary()` with parsed data
- Test `format_implementation_summary()` with different completion states

### Integration Tests
- Run ralph-loop with Markdown spec (3-5 tasks), verify summaries after each iteration
- Run ralph-loop with JSON spec (3-5 stories), verify summaries
- Run ralph-loop with `--summary-only`, verify Claude output is suppressed but summaries show
- Run ralph-loop with `--no-summaries`, verify no summaries appear
- Run feature-loop end-to-end with `--skip-review`, verify implementation summary appears
- Run feature-loop with review enabled (if ACR available), verify ACR summaries appear
- Verify progress files contain all summaries with correct formatting

### Edge Cases
- Ralph-loop iteration with no file changes (summary should say "No files modified")
- Ralph-loop iteration that fails (exit code != 0, summary should show error status in red)
- ACR review with zero findings (LGTM summary)
- ACR review with many findings across many files (summary should be concise, not overwhelming)
- Ralph-loop reaching max iterations before completion (final summary should indicate incomplete)
- Feature-loop reaching max review iterations (should handle gracefully)
- Empty spec files or malformed specs (should handle errors gracefully)
- Running in environment without color support (no ANSI codes should be used)
- Running with output piped to file (colors should be auto-disabled)
- Progress files that don't exist or are unreadable
- Git repository in detached HEAD state or with merge conflicts

## Acceptance Criteria
- Ralph-loop displays a clear, structured summary after each iteration showing task, status, files changed, and progress
- Summaries use color coding (when supported) for quick visual scanning: green for success, yellow for warnings, red for errors
- Ralph-loop summaries are appended to progress file with timestamps
- Feature-loop displays implementation summary after ralph-loop completes, showing iterations, tasks completed, and files modified
- Feature-loop displays ACR findings summary after each review iteration before running triage
- ACR summaries show total findings, affected files with counts, and LGTM status
- All summaries have clear visual boundaries (separator lines) making them easy to spot in output
- Summaries are concise (fit on one screen) yet informative
- `--summary-only` flag works in ralph-loop: suppresses verbose output, shows only summaries
- `--no-summaries` flag works in ralph-loop: disables all summary output for backwards compatibility
- Progress files remain human-readable and contain useful historical data
- All existing functionality continues to work without regressions (checkpoints, resume, configuration, etc.)
- Documentation is updated with examples and flag descriptions
- Color codes are automatically disabled when output is piped or terminal doesn't support colors

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Create a test Markdown spec for ralph-loop testing
cat > /tmp/test-observability-spec.md << 'EOF'
# Feature: Test Observability

## Step by Step Tasks

### Step 1: Create a test file
- Create a file called observability-test.txt with content "iteration 1"

### Step 2: Modify the test file
- Append "iteration 2" to observability-test.txt

### Step 3: Create a second file
- Create observability-test2.txt with content "final iteration"
EOF

# Test ralph-loop with the test spec
# Verify: summaries appear after each iteration, showing task names and file changes
./plugins/spawn/scripts/ralph-loop --spec /tmp/test-observability-spec.md --max-iterations 5

# Verify progress file was created and contains summaries
test -f /tmp/test-observability-spec-progress.txt && echo "Progress file exists" || echo "ERROR: Progress file missing"
grep -c "Iteration.*Summary" /tmp/test-observability-spec-progress.txt || echo "ERROR: No summaries in progress file"

# Test ralph-loop with --summary-only flag (should show only summaries, not verbose Claude output)
rm -f /tmp/test-observability-spec-progress.txt observability-test.txt observability-test2.txt
./plugins/spawn/scripts/ralph-loop --spec /tmp/test-observability-spec.md --max-iterations 2 --summary-only 2>&1 | tee /tmp/summary-only-output.txt
# Manually verify: output should show only summaries, not full Claude conversation

# Test ralph-loop with --no-summaries flag (should suppress summaries)
rm -f /tmp/test-observability-spec-progress.txt observability-test.txt observability-test2.txt
./plugins/spawn/scripts/ralph-loop --spec /tmp/test-observability-spec.md --max-iterations 2 --no-summaries 2>&1 | tee /tmp/no-summaries-output.txt
# Manually verify: no summary sections should appear in output

# Test ralph-loop --help shows new flags
./plugins/spawn/scripts/ralph-loop --help | grep -E "summary-only|no-summaries"
test $? -eq 0 && echo "Flags documented in help" || echo "ERROR: Flags not in help text"

# Test feature-loop with a simple feature (skip review to focus on implementation summary)
# Verify: implementation summary appears after ralph-loop phase completes
./plugins/sdlc/scripts/feature-loop "Add a simple hello world function to a new file" \
  --max-implement-iterations 3 --skip-review --no-resume --verbose 2>&1 | tee /tmp/feature-loop-output.txt

# Check that implementation summary appears in output
grep -i "implementation.*complete" /tmp/feature-loop-output.txt && echo "Implementation summary found" || echo "WARNING: No implementation summary"

# Test feature-loop with review (if acr is available and you want to test ACR summaries)
# This requires acr CLI to be installed
if command -v acr > /dev/null 2>&1; then
  echo "Testing feature-loop with review..."
  ./plugins/sdlc/scripts/feature-loop "Add a simple utility function" \
    --max-implement-iterations 2 --max-review-iterations 2 --no-resume --verbose 2>&1 | tee /tmp/feature-loop-review-output.txt

  # Check for ACR summaries
  grep -i "review.*summary" /tmp/feature-loop-review-output.txt && echo "Review summaries found" || echo "WARNING: No review summaries"
else
  echo "Skipping ACR review test (acr not installed)"
fi

# Test error handling: invalid spec path
./plugins/spawn/scripts/ralph-loop --spec /tmp/nonexistent-spec.md 2>&1 | grep -i "not found"
test $? -eq 0 && echo "Error handling works" || echo "ERROR: Did not catch invalid spec"

# Test color output detection (when piped, colors should be disabled)
./plugins/spawn/scripts/ralph-loop --spec /tmp/test-observability-spec.md --max-iterations 1 2>&1 | cat > /tmp/piped-output.txt
# Manually check /tmp/piped-output.txt for ANSI escape codes - there should be none

# Clean up test files
rm -f /tmp/test-observability-spec.md /tmp/test-observability-spec-progress.txt
rm -f observability-test.txt observability-test2.txt
rm -f /tmp/summary-only-output.txt /tmp/no-summaries-output.txt
rm -f /tmp/feature-loop-output.txt /tmp/feature-loop-review-output.txt
rm -f /tmp/piped-output.txt
rm -f .feature-loop-state.json

echo ""
echo "Validation complete! Review output above for any errors."
```

## Notes
- **Color support detection**: Use `os.isatty(sys.stdout.fileno())` in Python to detect if stdout is a terminal. Also check `TERM` environment variable is not "dumb".
- **Progress file format**: Keep plain text without ANSI codes for grep-friendliness and compatibility.
- **ACR output parsing**: ACR output format may vary. Parse defensively and handle cases where expected patterns aren't found. If parsing fails, show a generic summary like "Review complete - see output above for details."
- **Performance**: Summaries should add minimal overhead. Git status and file parsing are fast operations.
- **Backwards compatibility**: The `--no-summaries` flag ensures users who prefer the old behavior can disable the feature.
- **Future enhancements**:
  - Structured JSON output mode for machine parsing (`--output-format json`)
  - Real-time dashboard/TUI mode showing live progress (`--watch`)
  - Timing metrics (time per iteration, estimated time remaining)
  - Export summaries to Markdown or HTML for reporting
- **Testing note**: Some validation commands require `acr` CLI to be installed. If not available, those tests can be skipped.
- **Git integration**: The feature assumes the project is in a git repository. Handle gracefully if not (show a message, don't crash).
