# Feature: Review Command for SDLC Plugin

## Feature Description
Create a new `/sdlc:review` command that runs an automated code review loop similar to the review phase in the `feature-loop` script. This command will continuously run ACR (Automated Code Review) with specified configuration flags, diagnose whether findings are real issues or false positives, and take appropriate action (fix real issues, add comments explaining false positives) until ACR returns only false positives or exits successfully (LGTM).

The command provides a standalone way to perform iterative code review and triage without needing to run the full feature-loop workflow (planning + implementation + review).

## User Story
As a developer
I want to run an iterative code review loop independently
So that I can review and fix code quality issues without going through the full feature-loop workflow

## Problem Statement
Currently, the automated code review loop is only accessible as part of the `feature-loop` script, which requires running the planning and implementation phases first. Developers need a standalone command to:
1. Run code review on existing code changes
2. Automatically diagnose and fix real issues
3. Add explanatory comments for false positives
4. Iterate until code passes review or max iterations are reached

This functionality is valuable for:
- Reviewing code after manual development
- Re-running review after fixing issues from a previous feature-loop
- Running review with different configurations
- Quick quality checks on branches before creating PRs

## Solution Statement
Create a new `/sdlc:review` command that:
1. Accepts command-line arguments for review configuration (max iterations, number of reviewers, model selection)
2. Runs ACR with the flags: `--local -a claude -s claude -r 5` (configurable via args and `.claude-kit`)
3. Parses ACR output to extract findings
4. Displays a structured review summary before triage
5. Invokes Claude to diagnose findings (real issues vs false positives)
6. Fixes real issues and adds explanatory comments for false positives
7. Repeats the review cycle until LGTM or max iterations reached
8. Logs summaries to `.review-loop.log` for historical reference

The command will reuse existing functions from `feature-loop` script for review execution, parsing, summary formatting, and triage.

## Relevant Files

**Existing files to reference:**

- `plugins/sdlc/scripts/feature-loop` - Contains the review loop implementation (lines 1060-1173)
  - `run_review()` function - Executes ACR with configuration
  - `triage_and_fix_issues()` function - Diagnoses and fixes findings
  - `parse_acr_output()` function - Parses ACR output
  - `format_acr_summary()` function - Formats review summaries
  - Configuration loading, logging, and checkpoint logic

- `plugins/sdlc/.claude-plugin/plugin.json` - Plugin metadata that lists available commands

- `plugins/sdlc/commands/feature.md` - Example command structure for reference
- `plugins/sdlc/commands/implement.md` - Example command structure for reference
- `plugins/sdlc/commands/bug.md` - Example command structure for reference
- `plugins/sdlc/commands/chore.md` - Example command structure for reference

- `plugins/sdlc/README.md` - Documentation that needs updating with new command

### New Files

- `plugins/sdlc/commands/review.md` - Command prompt/instructions for `/sdlc:review`
- `plugins/sdlc/scripts/review-loop` - Standalone review loop script (Python with uv)

## Implementation Plan

### Phase 1: Foundation
Extract and adapt the review loop logic from `feature-loop` into a standalone, reusable script. The new script should:
- Accept command-line arguments for configuration (max iterations, number of reviewers, model, verbosity)
- Reuse existing helper functions from feature-loop (run_review, triage_and_fix_issues, parse_acr_output, format_acr_summary)
- Support configuration via `.claude-kit` files
- Provide structured output summaries
- Log summaries to a dedicated review log file

### Phase 2: Core Implementation
Create the review-loop script with the following capabilities:
1. Validate that ACR CLI is available
2. Run ACR with configurable flags (--local, -a claude, -s claude, -r N)
3. Parse ACR output to identify findings
4. Display review summary before triage
5. Invoke Claude to diagnose and fix/comment on findings
6. Iterate until LGTM or max iterations reached
7. Handle errors gracefully and provide clear status messages

### Phase 3: Integration
1. Create the `/sdlc:review` command definition that invokes the review-loop script
2. Update plugin documentation with command usage and examples
3. Ensure configuration integration with existing `.claude-kit` config structure
4. Test the command end-to-end in various scenarios

## Step by Step Tasks

### Step 1: Create the review-loop script
**Status:** complete
- Create `plugins/sdlc/scripts/review-loop` as a Python script using uv (similar to feature-loop)
- Add shebang: `#!/usr/bin/env -S uv run --script`
- Add uv script header with dependencies (none needed beyond stdlib)
- Implement argument parsing with argparse:
  - `--max-iterations`, `-m`: Maximum review/fix cycles (default: 5)
  - `--num-reviewers`, `-r`: Number of ACR reviewers (default: 5)
  - `--model`: Model to use for triage (default: "claude")
  - `--verbose`, `-v`: Enable verbose logging
  - `--log`, `--log-file`: Path to log file for detailed execution capture
- Make the script executable with `chmod +x`

### Step 2: Implement configuration loading in review-loop
**Status:** complete
- Copy configuration loading functions from feature-loop:
  - `find_git_root()`
  - `discover_config_files()`
  - `load_config_file()`
  - `merge_configs()`
  - `validate_config()`
  - `load_configuration()`
- Adapt to load only relevant sections (acr config, review-specific settings)
- Support `.claude-kit` config precedence: home → git-root → cwd → CLI args

### Step 3: Implement review execution logic
**Status:** complete
- Copy and adapt review functions from feature-loop:
  - `log()` function for timestamped logging
  - `run_command()` function for subprocess execution
  - `check_command_exists()` function for CLI validation
  - `run_review()` function to execute ACR with configuration
  - `parse_acr_output()` function to extract findings
  - `format_acr_summary()` function for structured display
  - Color support functions (`supports_color()`, color constants)
  - `format_separator()` and `format_timestamp()` utilities

### Step 4: Implement triage logic
**Status:** complete
- Copy `triage_and_fix_issues()` function from feature-loop
- Ensure it properly invokes Claude with the diagnostic prompt
- Handle both real issues (fix code) and false positives (add comments)
- Log triage results

### Step 5: Implement the main review loop
**Status:** complete
- Create `main()` function that:
  - Parses arguments and loads configuration
  - Validates ACR CLI is available
  - Prints configuration header
  - Runs the review loop:
    - For iteration 1 to max_iterations:
      - Run ACR review
      - Parse and display summary
      - If exit_code == 0 (LGTM), break
      - If exit_code == 1 (findings), triage and fix
      - If exit_code >= 2 (error), exit with error
    - Handle max iterations reached case
  - Print completion status
  - Log summary to `.review-loop.log`

### Step 6: Add logging support
**Status:** complete
- Implement log file summary appending (reuse `log_summary_to_file()` pattern)
- Write review summaries (without color codes) to `.review-loop.log`
- Include timestamp and iteration number in log entries

### Step 7: Create the /sdlc:review command definition
**Status:** complete
- Create `plugins/sdlc/commands/review.md` with command prompt
- Follow the pattern from other commands (feature.md, bug.md, implement.md)
- Include instructions to:
  - Parse command arguments
  - Invoke the review-loop script with appropriate flags
  - Display results to user
  - Provide usage examples
- Document the expected behavior and options

### Step 8: Update plugin documentation
**Status:** complete
- Update `plugins/sdlc/README.md` to add `/sdlc:review` to the Commands section
- Include:
  - Command description and purpose
  - Usage examples (basic and advanced)
  - Configuration options
  - Integration with `.claude-kit` config
  - Default values and behavior
- Add review-loop script to Scripts section

### Step 9: Test basic functionality
**Status:** complete
- Test the script directly: `./plugins/sdlc/scripts/review-loop --help`
- Verify argument parsing works correctly
- Test with minimal flags: `./plugins/sdlc/scripts/review-loop`
- Ensure it validates ACR CLI existence
- Check error messages are clear and helpful

### Step 10: Test review loop with ACR
**Status:** complete
- Make deliberate code changes that will trigger ACR findings
- Run review-loop and verify:
  - ACR executes with correct flags (--local -a claude -s claude -r 5)
  - Findings are parsed and displayed correctly
  - Summary format is clear and readable
  - Triage invokes Claude properly
  - Fixes are applied or comments are added
  - Loop continues until LGTM or max iterations

### Step 11: Test configuration integration
**Status:** complete
- Create test `.claude-kit` config with custom values
- Verify CLI args override config values
- Test precedence: home → git-root → cwd → CLI
- Verify validation catches invalid config values
- Test `--no-verbose` to disable config verbose=true

### Step 12: Test the /sdlc:review command
**Status:** complete
- Test command invocation: `/sdlc:review`
- Test with arguments: `/sdlc:review --max-iterations 3 --model claude`
- Verify command properly invokes review-loop script
- Check that results are displayed to user
- Ensure error handling works correctly

### Step 13: Test edge cases
- Test with no git repo (should work)
- Test with no ACR installed (should error gracefully)
- Test with max iterations reached (should report status)
- Test with LGTM on first iteration (should exit cleanly)
- Test with verbose flag (should show detailed output)
- Test with log file flag (should create log file)

### Step 14: Validate with feature-loop integration check
- Verify review-loop can be used standalone OR as part of feature-loop
- Check that both scripts use consistent configuration
- Ensure log file formats are compatible
- Validate that color output works in both contexts

### Step 15: Run validation commands
- Execute all validation commands listed below
- Verify zero errors and expected behavior
- Confirm documentation is accurate and complete

## Testing Strategy

### Unit Tests
Since this is a command-line tool integrated into the plugin system, testing will be primarily integration testing through actual usage. However, the following functions should be validated:
- Configuration loading and merging (test with multiple `.claude-kit` files)
- ACR output parsing (test with sample ACR output)
- Summary formatting (verify color codes and structure)
- Argument validation (test edge cases and invalid inputs)

### Edge Cases
1. **No ACR installed**: Should display clear error message and exit
2. **Max iterations reached**: Should report status and suggest manual review
3. **ACR error (exit code 2+)**: Should display error and exit gracefully
4. **First iteration LGTM**: Should exit immediately with success message
5. **Empty review output**: Should handle gracefully
6. **Invalid configuration**: Should provide helpful validation errors
7. **No git repo**: Should work fine (review doesn't require git)
8. **No findings but exit code 1**: Should handle unexpected ACR behavior
9. **Triage fails**: Should continue loop and try again next iteration
10. **Interrupted execution**: Should handle KeyboardInterrupt gracefully

## Acceptance Criteria
1. ✓ `/sdlc:review` command is available in the SDLC plugin
2. ✓ Command runs ACR with flags: `--local -a claude -s claude -r 5` (or configured values)
3. ✓ Review findings are parsed and displayed in a structured summary
4. ✓ Triage correctly diagnoses real issues vs false positives
5. ✓ Real issues are fixed, false positives get explanatory comments
6. ✓ Loop continues until LGTM or max iterations reached
7. ✓ Configuration is loaded from `.claude-kit` files with correct precedence
8. ✓ CLI arguments override configuration file values
9. ✓ Review summaries are logged to `.review-loop.log`
10. ✓ Error handling is robust and provides clear messages
11. ✓ Documentation is complete and accurate in README.md
12. ✓ Script is executable and follows uv script conventions
13. ✓ Command works both standalone and is consistent with feature-loop behavior
14. ✓ Verbose mode provides detailed execution visibility
15. ✓ Color output works correctly in terminals that support it

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# 1. Verify review-loop script exists and is executable
test -x plugins/sdlc/scripts/review-loop && echo "✓ Script exists and is executable"

# 2. Verify review-loop help works
./plugins/sdlc/scripts/review-loop --help

# 3. Verify review.md command definition exists
test -f plugins/sdlc/commands/review.md && echo "✓ Command definition exists"

# 4. Verify documentation updated
grep -q "sdlc:review" plugins/sdlc/README.md && echo "✓ README updated with review command"

# 5. Run review-loop with no ACR (should fail gracefully if ACR not installed)
./plugins/sdlc/scripts/review-loop --max-iterations 1 2>&1 | grep -q "acr" && echo "✓ Validates ACR requirement"

# 6. Test configuration loading (requires .claude-kit file with acr config)
# This is a manual check to ensure config is loaded correctly

# 7. Test the command via Claude CLI (requires Claude CLI and plugin loaded)
# Manual test: claude --plugin-dir plugins/sdlc
# Then run: /sdlc:review --max-iterations 1

# 8. Verify script follows uv conventions
head -n 5 plugins/sdlc/scripts/review-loop | grep -q "uv run --script" && echo "✓ Uses uv script format"

# 9. Verify Python syntax is valid
python3 -m py_compile plugins/sdlc/scripts/review-loop

# 10. Check that review-loop imports no external dependencies beyond stdlib
grep -E "^import|^from" plugins/sdlc/scripts/review-loop | grep -v "^import (argparse|json|os|re|subprocess|sys|datetime|pathlib|time)" | grep -v "^from (datetime|pathlib|typing)" && echo "✗ Unexpected dependencies" || echo "✓ Only stdlib dependencies"

# 11. Verify configuration validation works
# Manual test: create invalid .claude-kit and run review-loop to check error handling

# 12. Test that review summaries include expected sections
# Manual test: run review-loop and verify output format

# 13. Verify log file creation
# Manual test: run with --log flag and verify file is created with valid JSON/text format

# 14. Check that triage prompt is comprehensive
grep -q "false positive" plugins/sdlc/scripts/review-loop && echo "✓ Triage handles false positives"
grep -q "real issue" plugins/sdlc/scripts/review-loop && echo "✓ Triage handles real issues"

# 15. Ensure color support detection works
grep -q "supports_color" plugins/sdlc/scripts/review-loop && echo "✓ Color support implemented"
```

## Notes

### Implementation Notes
- The review-loop script should be nearly identical to the review phase of feature-loop (lines 1507-1574)
- Maximum code reuse from feature-loop to maintain consistency and reduce maintenance burden
- The script should be usable both standalone and potentially callable from other scripts
- Consider extracting shared functions into a library module if there's significant duplication

### Configuration Integration
- The `.claude-kit` config should support an `acr` section with `num_reviewers` setting
- Default to 5 reviewers matching the feature request (--local -a claude -s claude -r 5)
- The `-a claude -s claude` flags appear to be analyzer/summarizer model selection - these should also be configurable
- Consider adding `acr.analyzer_model` and `acr.summarizer_model` config options for flexibility

### Future Enhancements
- Add support for `--resume` functionality similar to feature-loop (save checkpoint after each iteration)
- Add `--dry-run` mode to see what would be reviewed without making changes
- Add `--summary-only` flag to show only summaries without verbose ACR output
- Support custom ACR config files via `--acr-config` argument
- Add metrics reporting (total findings, fix rate, false positive rate, etc.)
- Integration with PR workflows (run review-loop before creating PR)

### ACR Flags Clarification
Based on the feature request, the default ACR invocation should be:
```bash
acr --local -a claude -s claude -r 5
```

Where:
- `--local`: Run locally (not on remote server)
- `-a claude`: Use "claude" as analyzer model
- `-s claude`: Use "claude" as summarizer model
- `-r 5`: Use 5 reviewers

These should all be configurable via CLI args and `.claude-kit` config.
