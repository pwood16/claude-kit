# Feature: Enhanced Loop Observability with Iteration Summaries

## Feature Description
Enhance ralph-loop and feature-loop workflows with comprehensive, real-time observability by outputting detailed summaries after each iteration. Users will see clear, structured reports showing what each ralph-loop iteration accomplished and what each ACR review found, before moving to the next iteration. This transforms verbose log streams into digestible progress updates that make long-running automated workflows transparent and easier to monitor.

## User Story
As a developer running feature-loop workflows
I want to see a clear summary of what ralph-loop accomplished during each iteration
And I want to see what the ACR loop found during each review run
So that I can understand progress at a glance, identify issues quickly, and have confidence in the automation without parsing verbose logs.

## Problem Statement
Currently, ralph-loop and feature-loop run iterations continuously with verbose output but lack clear boundaries and summaries between iterations. Users experience:

1. **Unclear iteration boundaries**: When one iteration ends and the next begins is not visually obvious
2. **No ralph-loop iteration summaries**: Hard to tell which task was completed, what files changed, or if the iteration succeeded
3. **No ACR findings summaries**: Review results aren't summarized before triage, making it unclear what issues were found and in which files
4. **Poor progress tracking**: No clear indication of overall progress (X of Y tasks completed)
5. **Difficult debugging**: When issues occur, it's hard to identify which iteration caused them
6. **No historical record**: Progress logs may not capture structured summaries for post-mortem analysis

This makes monitoring long-running workflows difficult and reduces confidence in the automation.

## Solution Statement
Implement comprehensive iteration summaries for both ralph-loop and the ACR review loop:

**Ralph-loop iteration summaries:**
- Display after each iteration completes, showing:
  - Iteration number and timestamp
  - Task that was targeted (from spec h3 heading or JSON story)
  - Task completion status (complete/incomplete)
  - Files modified, added, or deleted during the iteration
  - Exit code and error information
  - Overall progress (X of Y tasks complete)
- Use color coding (green=success, yellow=warning, red=error) for quick scanning
- Add visual separators between iterations
- Write summaries to progress file for historical reference

**ACR review loop summaries:**
- Display after each ACR run completes, before triage begins, showing:
  - Review iteration number
  - Total findings count
  - Files affected with finding count per file
  - Finding types/categories (if detectable in output)
  - LGTM status or indication that fixes are needed
- Color-coded for quick scanning (green=LGTM, yellow/red=issues found)
- Clear transition before triage phase

**Additional features:**
- `--summary-only` flag: Show only summaries, suppress verbose Claude output
- `--no-summaries` flag: Disable summaries for backwards compatibility
- Auto-detect color support (disable when piping output)
- Log all summaries to appropriate progress files

## Relevant Files
Use these files to implement the feature:

### Existing Files

**plugins/spawn/scripts/ralph-loop** (Python script)
- Main iteration loop (lines 471-531) - outputs iteration summaries
- Already has comprehensive summary functions implemented
- Has `--summary-only` and `--no-summaries` flags
- Relevance: Core loop that needs to output iteration summaries after each run
- Status: Implementation appears complete based on progress file, needs validation

**plugins/sdlc/scripts/feature-loop** (Python script)
- Orchestrates planning, implementation (ralph-loop), and review (ACR) phases
- Lines 443-468: `run_implement()` - calls ralph-loop
- Lines 470-504: `run_review()` - runs ACR review
- Lines 533-973: Review loop logic with ACR triage
- Lines 631-699: ACR summary display (appears to be implemented)
- Lines 867-937: Implementation summary display (appears to be implemented)
- Relevance: Orchestrator that displays implementation and ACR summaries
- Status: Implementation appears complete, needs validation

**plugins/spawn/README.md**
- Documentation for ralph-loop and spawn plugin
- Should document iteration summary format and flags
- Status: Updated in Step 12 of previous implementation

**plugins/sdlc/README.md**
- Documentation for feature-loop and SDLC workflows
- Should document implementation and ACR summaries
- Status: Updated in Step 12 of previous implementation

### New Files
None required - enhancements to existing scripts only.

## Implementation Plan

### Phase 1: Validation & Testing
Validate that all implemented features work correctly and fix any issues found during testing. Ensure ralph-loop iteration summaries appear correctly, ACR summaries display properly, and all command-line flags function as expected.

### Phase 2: Gap Analysis & Fixes
Identify any gaps in the current implementation (particularly ACR summary display which wasn't fully tested). Fix any bugs or missing functionality discovered during validation.

### Phase 3: Integration Testing
Run end-to-end workflows with real features to ensure all summaries appear at the correct moments, are properly formatted, and provide value to users. Verify logging to progress files works correctly.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Validate ralph-loop iteration summaries
**Status:** pending
- Run ralph-loop with a test spec to verify iteration summaries work correctly
- Create a test Markdown spec with 3-4 simple tasks
- Run ralph-loop and observe that summaries appear after each iteration
- Verify summaries include: iteration number, timestamp, task name, status, files changed, exit status, progress
- Verify summaries use color coding appropriately
- Verify summaries are appended to progress file
- Document any issues or missing functionality

### Step 2: Validate ralph-loop command-line flags
**Status:** pending
- Test `--summary-only` flag: verify verbose output is suppressed but summaries still appear
- Test `--no-summaries` flag: verify summaries are completely disabled
- Test `--help` output includes documentation for both flags
- Verify flags work correctly with both Markdown and JSON spec formats
- Document any issues

### Step 3: Validate feature-loop implementation summary
**Status:** pending
- Run feature-loop with a simple test feature using `--skip-review` flag
- Verify implementation summary appears after ralph-loop completes
- Summary should show: timestamp, total iterations, tasks completed/remaining, files modified
- Verify summary has clear visual boundaries (separator lines)
- Verify summary uses appropriate color coding
- Document any issues

### Step 4: Validate feature-loop ACR summary display
**Status:** pending
- Run feature-loop with a test feature that requires code review
- Use `--max-review-iterations 3` to limit review cycles
- Verify ACR summary appears after each review run, before triage
- Summary should show: review iteration, findings count, affected files, finding types, status
- Verify summary uses color coding (green for LGTM, yellow/red for findings)
- If ACR summary doesn't appear or is incomplete, identify what needs to be fixed
- Document findings

### Step 5: Fix any ACR summary display issues
**Status:** pending
- Based on Step 4 findings, fix any issues with ACR summary display
- Ensure `parse_acr_output()` function correctly extracts findings data
- Ensure `format_acr_summary()` function formats data properly
- Ensure summary is displayed at the correct point in the review loop (after run_review(), before triage)
- Test with both successful reviews (LGTM) and reviews with findings

### Step 6: Validate progress file logging
**Status:** pending
- Verify ralph-loop progress files contain all iteration summaries with timestamps
- Verify summaries in progress files don't contain ANSI color codes (grep-friendly)
- Check if feature-loop logs implementation and ACR summaries (to .feature-loop-*.log or similar)
- If logging is missing, implement it
- Verify logged summaries are human-readable and useful for post-mortem analysis

### Step 7: Test edge cases
**Status:** pending
- Test ralph-loop iteration with no file changes (summary should handle gracefully)
- Test ralph-loop iteration that fails (exit code != 0, summary should show error in red)
- Test ACR review with zero findings (LGTM summary should appear)
- Test ACR review with many findings across many files (summary should be concise)
- Test ralph-loop reaching max iterations before completion
- Test color output when piped to a file (colors should be disabled automatically)
- Document any issues found

### Step 8: Test end-to-end workflow
**Status:** pending
- Run complete feature-loop workflow with a moderately complex feature
- Use realistic limits: `--max-implement-iterations 10 --max-review-iterations 5`
- Observe all summaries throughout the workflow:
  - Ralph-loop iteration summaries during implementation
  - Implementation summary after ralph-loop completes
  - ACR summaries after each review iteration
- Verify workflow is easier to follow with summaries than without
- Verify no regressions in existing functionality (checkpoints, resume, etc.)
- Document user experience and any issues

### Step 9: Review and update documentation
**Status:** pending
- Review plugins/spawn/README.md for accuracy and completeness
- Review plugins/sdlc/README.md for accuracy and completeness
- Ensure examples in documentation match actual output format
- Ensure all flags and features are documented
- Add troubleshooting section if needed
- Update any outdated information

### Step 10: Run full validation command suite
**Status:** pending
- Execute all validation commands from the Validation Commands section
- Verify every command completes without errors
- Review output for any warnings or unexpected behavior
- Fix any issues discovered
- Mark feature as complete when all validation passes

## Testing Strategy

### Unit Tests
- Test color support detection with various TERM values and TTY states
- Test git status parsing with different repository states
- Test task extraction from both Markdown and JSON specs
- Test ACR output parsing with various ACR output formats
- Test summary formatting functions with different input data
- Test command-line flag parsing and behavior

### Integration Tests
- Run ralph-loop end-to-end with Markdown spec (verify summaries)
- Run ralph-loop end-to-end with JSON spec (verify summaries)
- Run ralph-loop with `--summary-only` (verify output suppression)
- Run ralph-loop with `--no-summaries` (verify summary suppression)
- Run feature-loop with `--skip-review` (verify implementation summary)
- Run feature-loop with review enabled (verify ACR summaries)
- Verify all progress file logging works correctly

### Edge Cases
- Ralph-loop iteration with no file changes
- Ralph-loop iteration that crashes or times out
- ACR review with zero findings (LGTM)
- ACR review with 50+ findings (summary should remain concise)
- Running in environment without git
- Running in environment without color support (TERM=dumb)
- Output piped to file (colors should be disabled)
- Progress files that are corrupted or unreadable
- Spec files that are malformed or incomplete
- Max iterations reached before completion

## Acceptance Criteria
- Ralph-loop displays clear, structured summaries after each iteration showing task, status, files changed, and progress
- Summaries use color coding when supported: green for success, yellow for warnings, red for errors
- Ralph-loop summaries are appended to progress files with timestamps (no color codes in files)
- Feature-loop displays implementation summary after ralph-loop completes, showing iterations, tasks completed, files modified
- Feature-loop displays ACR findings summary after each review iteration, before running triage
- ACR summaries show total findings, affected files with counts, finding types, and LGTM status
- All summaries have clear visual boundaries (separator lines) making them easy to spot
- Summaries are concise (fit on screen) yet informative
- `--summary-only` flag works: suppresses verbose output, shows only summaries
- `--no-summaries` flag works: disables all summary output
- Progress files remain human-readable and grep-friendly
- Color codes are automatically disabled when output is piped or terminal doesn't support colors
- All existing functionality continues to work (no regressions)
- Documentation is accurate and includes examples

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Create test spec for ralph-loop validation
cat > /tmp/test-observability.md << 'EOF'
# Feature: Test Observability

## Step by Step Tasks

### Step 1: Create a test file
**Status:** pending
- Create a file called test-observability-file.txt with content "iteration 1"

### Step 2: Modify the test file
**Status:** pending
- Append "iteration 2" to test-observability-file.txt

### Step 3: Create a second file
**Status:** pending
- Create test-observability-file2.txt with content "final iteration"
EOF

# Test 1: Ralph-loop with iteration summaries (default behavior)
echo "=== Test 1: Ralph-loop with iteration summaries ==="
./plugins/spawn/scripts/ralph-loop --spec /tmp/test-observability.md --max-iterations 5
echo ""
echo "Expected: Iteration summaries should appear after each iteration"
echo "Verify manually that summaries include: iteration #, timestamp, task, status, files, progress"
echo ""

# Test 2: Verify progress file contains summaries
echo "=== Test 2: Progress file validation ==="
test -f /tmp/test-observability-progress.txt && echo "✓ Progress file exists" || echo "✗ ERROR: Progress file missing"
summary_count=$(grep -c "Iteration.*Summary" /tmp/test-observability-progress.txt 2>/dev/null || echo "0")
echo "Found $summary_count iteration summaries in progress file"
test "$summary_count" -gt 0 && echo "✓ Progress file contains summaries" || echo "✗ ERROR: No summaries in progress file"
echo ""

# Test 3: Ralph-loop with --summary-only flag
echo "=== Test 3: Ralph-loop --summary-only ==="
rm -f /tmp/test-observability-progress.txt test-observability-file.txt test-observability-file2.txt
./plugins/spawn/scripts/ralph-loop --spec /tmp/test-observability.md --max-iterations 3 --summary-only
echo ""
echo "Expected: Only summaries visible, no verbose Claude conversation output"
echo "Verify manually that verbose output was suppressed"
echo ""

# Test 4: Ralph-loop with --no-summaries flag
echo "=== Test 4: Ralph-loop --no-summaries ==="
rm -f /tmp/test-observability-progress.txt test-observability-file.txt test-observability-file2.txt
output=$(./plugins/spawn/scripts/ralph-loop --spec /tmp/test-observability.md --max-iterations 2 --no-summaries 2>&1)
if echo "$output" | grep -q "Summary"; then
  echo "✗ ERROR: Summaries appeared despite --no-summaries flag"
else
  echo "✓ Summaries correctly suppressed"
fi
echo ""

# Test 5: Ralph-loop --help shows new flags
echo "=== Test 5: Ralph-loop help documentation ==="
help_output=$(./plugins/spawn/scripts/ralph-loop --help 2>&1)
echo "$help_output" | grep -q "summary-only" && echo "✓ --summary-only documented" || echo "✗ ERROR: --summary-only not in help"
echo "$help_output" | grep -q "no-summaries" && echo "✓ --no-summaries documented" || echo "✗ ERROR: --no-summaries not in help"
echo ""

# Test 6: Feature-loop with implementation summary (skip review)
echo "=== Test 6: Feature-loop implementation summary ==="
./plugins/sdlc/scripts/feature-loop "Add a simple test function called hello_world that returns 'Hello, World!'" \
  --max-implement-iterations 5 --skip-review --no-resume --verbose 2>&1 | tee /tmp/feature-loop-test.txt
echo ""
if grep -q -i "implementation.*complete\|Implementation Phase Complete" /tmp/feature-loop-test.txt; then
  echo "✓ Implementation summary found"
else
  echo "✗ WARNING: Implementation summary not found in output"
fi
echo ""

# Test 7: Feature-loop with ACR review summaries
echo "=== Test 7: Feature-loop ACR review summaries ==="
if command -v acr > /dev/null 2>&1; then
  echo "ACR available, testing review loop..."
  ./plugins/sdlc/scripts/feature-loop "Add a goodbye_world function that returns 'Goodbye, World!'" \
    --max-implement-iterations 3 --max-review-iterations 2 --no-resume --verbose 2>&1 | tee /tmp/feature-loop-review-test.txt
  echo ""
  if grep -q -i "review.*summary\|Code Review Summary" /tmp/feature-loop-review-test.txt; then
    echo "✓ ACR summaries found"
  else
    echo "✗ WARNING: ACR summaries not found in output"
  fi
else
  echo "⊘ Skipping ACR test (acr not installed)"
fi
echo ""

# Test 8: Color output when piped
echo "=== Test 8: Color output detection ==="
rm -f /tmp/test-observability-progress.txt test-observability-file.txt test-observability-file2.txt
./plugins/spawn/scripts/ralph-loop --spec /tmp/test-observability.md --max-iterations 1 2>&1 | cat > /tmp/piped-output.txt
if grep -q $'\033\[' /tmp/piped-output.txt; then
  echo "⚠ WARNING: ANSI color codes found in piped output (may be intentional)"
else
  echo "✓ No color codes in piped output"
fi
echo ""

# Test 9: Error handling with invalid spec
echo "=== Test 9: Error handling ==="
error_output=$(./plugins/spawn/scripts/ralph-loop --spec /tmp/nonexistent-spec.md 2>&1)
if echo "$error_output" | grep -q -i "not found\|does not exist\|error"; then
  echo "✓ Error handling works for invalid spec"
else
  echo "✗ WARNING: Error message not clear for invalid spec"
fi
echo ""

# Clean up test files
echo "=== Cleanup ==="
rm -f /tmp/test-observability.md /tmp/test-observability-progress.txt
rm -f test-observability-file.txt test-observability-file2.txt
rm -f /tmp/feature-loop-test.txt /tmp/feature-loop-review-test.txt
rm -f /tmp/piped-output.txt
rm -f .feature-loop-state.json
echo "✓ Test files cleaned up"
echo ""

echo "========================================"
echo "Validation Complete"
echo "========================================"
echo "Review the output above for any errors or warnings."
echo "All ✓ marks indicate passing tests."
echo "All ✗ marks indicate failures that need investigation."
echo "All ⚠ marks indicate warnings that may need attention."
```

## Notes
- **Previous implementation**: This feature was previously implemented (specs/issue-loop-observability-output.md) with Steps 1-14 marked complete. This plan focuses on validation and ensuring everything works correctly end-to-end.
- **ACR integration**: Step 8 of the previous implementation was marked complete but ACR summaries weren't fully tested. This plan prioritizes validating ACR summary display in Step 4-5.
- **Color support**: Colors should be automatically disabled when output is piped or TERM is "dumb". Use `os.isatty(sys.stdout.fileno())` and check `NO_COLOR` environment variable.
- **Progress file format**: Plain text without ANSI codes for grep-friendliness and cross-platform compatibility.
- **Backwards compatibility**: `--no-summaries` flag ensures users can disable the feature if needed.
- **Performance**: Summaries add minimal overhead (git status and file parsing are fast).
- **Future enhancements**:
  - JSON output mode for machine parsing (`--output-format json`)
  - Real-time TUI/dashboard mode (`--watch`)
  - Timing metrics (time per iteration, ETA)
  - Export summaries to Markdown/HTML for reporting
  - Integration with CI/CD systems (GitHub Actions annotations)
