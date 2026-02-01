# Feature: Claude Model Selection and Enhanced Log Capture

## Feature Description
Update the ralph-loop and feature-loop scripts to use Claude models as the default agent and summarizer (replacing any codex references), and add comprehensive log capture functionality when a log parameter is passed. This will enable better debugging, performance analysis, and data-driven improvements to the scripts.

## User Story
As a developer using the SDLC automation scripts
I want to use Claude models by default and optionally capture detailed logs
So that I can debug runs effectively and contribute data to improve script performance

## Problem Statement
Currently, the scripts hardcode the `claude` CLI command without explicit model selection, making it unclear which model is being used and preventing users from choosing specific Claude models. Additionally, while some logging exists (progress files, summary files), there is no comprehensive log capture mechanism that records the full execution trace including:
- All Claude agent invocations and responses
- Command execution details
- Timing information
- Error traces
- Configuration snapshots

This lack of comprehensive logging makes it difficult to:
1. Debug failed runs
2. Analyze performance bottlenecks
3. Understand agent decision-making
4. Improve prompts and workflows based on data

## Solution Statement
Extend the configuration system and CLI arguments to support:
1. **Model Selection**: Add `model` configuration option to `.claude-kit` config and CLI arguments for both scripts, with "claude" as the default (maintaining backwards compatibility)
2. **Log Capture**: Add optional `--log` or `--log-file` parameter that enables comprehensive structured logging to a specified file, capturing:
   - All agent invocations with prompts and responses
   - Subprocess commands and outputs
   - Timing data (iteration durations, total runtime)
   - Configuration snapshots
   - Error details with full stack traces

The implementation will maintain backwards compatibility while providing opt-in detailed logging for debugging and analysis.

## Relevant Files
Use these files to implement the feature:

- **plugins/spawn/scripts/ralph-loop.py** (lines 356-394)
  - Contains `run_claude_iteration()` function that invokes the Claude CLI
  - Needs model parameter support and log capture integration
  - Already has argument parsing (lines 44-83) that needs extension

- **plugins/sdlc/scripts/feature-loop** (lines 339-415)
  - Contains `run_plan()` function that invokes Claude CLI for planning
  - Needs model parameter support and log capture integration
  - Has comprehensive argument parsing (lines 1037-1150) that needs extension
  - Already has configuration loading system (lines 86-245) to extend

- **plugins/sdlc/scripts/feature-loop** (lines 732-752)
  - Contains `log_summary_to_file()` function for current logging
  - Provides pattern for structured log writing

### New Files
- **plugins/spawn/lib/logger.py** - Shared logging utilities for structured log capture (JSON format)
- **plugins/sdlc/lib/logger.py** - Symlink or copy of spawn logger for feature-loop usage

## Implementation Plan

### Phase 1: Foundation
Create a reusable logging infrastructure that both scripts can leverage. This includes a structured logger that can capture events in JSON format with timing information, and helper functions for common logging patterns.

### Phase 2: Core Implementation
Extend the configuration system to support model selection, add CLI arguments for model and log file specification, and integrate the logging infrastructure into the existing command execution paths without breaking current functionality.

### Phase 3: Integration
Update all Claude CLI invocations to use the configurable model parameter and log all relevant events when logging is enabled. Ensure backwards compatibility and add comprehensive documentation.

## Step by Step Tasks

### Create Shared Logging Infrastructure
**Status:** complete
- Create `plugins/spawn/lib/` directory if it doesn't exist
- Implement `plugins/spawn/lib/logger.py` with:
  - `StructuredLogger` class for JSON-based logging
  - Methods: `log_event()`, `log_iteration_start()`, `log_iteration_end()`, `log_command()`, `log_error()`
  - Automatic timestamp and duration tracking
  - Context manager support for timing blocks
  - Thread-safe file writing
- Write unit tests for the logger in `plugins/spawn/lib/test_logger.py`
- Create symlink or copy logger to `plugins/sdlc/lib/logger.py`

### Extend Configuration System
**Status:** complete
- Update `.claude-kit` example documentation with new `model` field:
  ```json
  {
    "feature_loop": {
      "model": "claude",
      "max_implement_iterations": 0,
      "max_review_iterations": 5
    },
    "ralph_loop": {
      "model": "claude"
    }
  }
  ```
- Update `feature-loop` configuration loading (lines 126-165) to parse and validate `model` field
- Add type hints for new configuration fields in TypedDict definitions

### Update ralph-loop CLI Arguments
- Add `--model` argument to `parse_arguments()` (after line 79):
  - Type: `str`
  - Default: `"claude"`
  - Help: "Model to use for agent invocations (default: claude)"
- Add `--log` / `--log-file` argument:
  - Type: `str`
  - Default: `None`
  - Help: "Path to log file for detailed execution capture (optional)"
- Update docstring and examples in epilog

### Update feature-loop CLI Arguments
- Add `--model` argument to main parser (after line 1145):
  - Type: `str`
  - Default from config or `"claude"`
  - Help: "Model to use for agent invocations"
- Add `--log` / `--log-file` argument:
  - Type: `str`
  - Default: `None`
  - Help: "Path to log file for detailed execution capture (optional)"
- Update configuration loading to include model parameter
- Update epilog with examples showing new parameters

### Integrate Logging in ralph-loop
- Import `StructuredLogger` from `lib.logger`
- Initialize logger in `run_ralph_loop()` if `--log` is provided
- Update `run_claude_iteration()` to:
  - Accept optional `logger` and `model` parameters
  - Use `model` parameter in CLI command instead of hardcoded "claude"
  - Log iteration start/end with timing
  - Log full command and output when logger is enabled
  - Log errors with full context
- Update all `run_claude_iteration()` call sites to pass model and logger

### Integrate Logging in feature-loop
- Import `StructuredLogger` from `lib.logger`
- Initialize logger in `main()` if `--log` is provided
- Update `run_plan()` to:
  - Accept optional `logger` and `model` parameters
  - Use `model` parameter in CLI command (line 348)
  - Log planning phase with timing
- Update `run_command()` wrapper to accept logger parameter
- Update code review invocations (lines 943-1033) to use model parameter and log events
- Update ralph-loop invocations (line 452) to pass model and log file parameters

### Update All Claude CLI Invocations
- Search for all `["claude",` command constructions
- Replace with model-aware construction: `[model, "--dangerously-skip-permissions", ...]`
- Ensure all paths support model parameter propagation
- Verify no hardcoded "claude" strings remain in command construction

### Add Documentation
- Update `plugins/spawn/README.md` with:
  - Model selection usage examples
  - Log capture usage examples
  - Log file format documentation
- Update `plugins/sdlc/README.md` with:
  - Model configuration in `.claude-kit`
  - CLI examples with `--model` and `--log`
  - Log file analysis tips
- Add `.claude-kit.example` file at repo root with all new options documented

### Run Validation Commands
Execute all validation commands to ensure the feature works correctly with zero regressions.

## Testing Strategy

### Unit Tests
- **Logger tests** (`plugins/spawn/lib/test_logger.py`):
  - Test JSON serialization of log events
  - Test timestamp generation
  - Test duration calculation
  - Test file writing (with temp files)
  - Test thread safety with concurrent writes
  - Test context manager timing

- **Configuration tests**:
  - Test parsing model field from `.claude-kit`
  - Test default model value when not configured
  - Test model precedence (CLI > config > default)
  - Test invalid model values (should warn or use default)

### Integration Tests
- **ralph-loop integration**:
  - Run with `--model claude --log /tmp/test.log` on a simple spec
  - Verify log file contains expected events
  - Verify model parameter is used in commands
  - Verify backwards compatibility (run without new parameters)

- **feature-loop integration**:
  - Run with model configured in `.claude-kit` and `--log` parameter
  - Verify planning, implementation, and review phases all log correctly
  - Verify model configuration is respected
  - Verify log file captures full workflow

### Edge Cases
- Missing log directory (should create parent directories)
- Log file without write permissions (should fail gracefully with clear error)
- Invalid model name (should warn but continue)
- Empty model string (should fall back to "claude")
- Concurrent log writes from multiple scripts (should not corrupt file)
- Very large outputs (should handle without memory issues)
- Unicode in outputs (should encode correctly)
- ANSI color codes in output (should preserve or strip based on config)

## Acceptance Criteria
- [ ] Both scripts accept `--model` CLI parameter (default: "claude")
- [ ] Both scripts accept `--log` or `--log-file` CLI parameter (optional)
- [ ] `.claude-kit` configuration supports `model` field in `feature_loop` and `ralph_loop` sections
- [ ] All Claude CLI invocations use the configured/specified model
- [ ] When `--log` is provided, comprehensive JSON-formatted logs are written including:
  - Iteration start/end with timestamps and durations
  - Full command invocations
  - Full agent outputs
  - Error details with stack traces
  - Configuration snapshot
- [ ] Backwards compatibility: scripts work identically when new parameters are not provided
- [ ] Log files are valid JSON (one event per line in JSONL format)
- [ ] Documentation updated with usage examples and log format specification
- [ ] All existing tests pass
- [ ] New unit tests for logger achieve >90% coverage
- [ ] Integration test validates end-to-end log capture

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Test ralph-loop with new parameters
cd /Users/cabewaldrop/dev/claude-kit
python plugins/spawn/scripts/ralph-loop.py --spec specs/issue-simple-hello-world.md --max-iterations 1 --model claude --log /tmp/ralph-test.log

# Verify log file was created and contains valid JSON
test -f /tmp/ralph-test.log && echo "Log file created" || echo "ERROR: Log file missing"
python -c "import json; [json.loads(line) for line in open('/tmp/ralph-test.log')]" && echo "Valid JSON" || echo "ERROR: Invalid JSON"

# Test feature-loop with config-based model
echo '{"feature_loop": {"model": "claude", "max_implement_iterations": 1, "max_review_iterations": 1}, "ralph_loop": {"model": "claude"}}' > /tmp/.claude-kit-test
cd /tmp && /Users/cabewaldrop/dev/claude-kit/plugins/sdlc/scripts/feature-loop "Add a simple test function" --log feature-loop-test.log --max-review-iterations 1

# Verify log file
test -f /tmp/feature-loop-test.log && echo "Feature-loop log created" || echo "ERROR: Log missing"

# Test backwards compatibility (no new parameters)
cd /Users/cabewaldrop/dev/claude-kit
python plugins/spawn/scripts/ralph-loop.py --spec specs/issue-simple-hello-world.md --max-iterations 1

# Run unit tests
python plugins/spawn/lib/test_logger.py

# Verify no regressions in existing functionality
python -m pytest plugins/ -v 2>/dev/null || echo "No pytest tests found (expected)"

# Test with invalid model name (should warn but continue)
python plugins/spawn/scripts/ralph-loop.py --spec specs/issue-simple-hello-world.md --max-iterations 1 --model invalid-model 2>&1 | grep -i "warn\|model" || echo "No warning shown"

# Verify configuration precedence
echo '{"ralph_loop": {"model": "config-model"}}' > .claude-kit
python plugins/spawn/scripts/ralph-loop.py --spec specs/issue-simple-hello-world.md --max-iterations 0 --model cli-model 2>&1 | head -20
rm .claude-kit
```

## Notes
- **Model naming**: The default "claude" relies on Claude CLI's default model selection. Consider adding validation to check if specified models are valid (e.g., "claude-3-opus", "claude-3-sonnet") though this requires knowledge of available models.
- **Log format**: Using JSONL (JSON Lines) format where each line is a complete JSON object. This allows streaming writes and easy parsing with tools like `jq`.
- **Performance**: Logging should have minimal performance impact. Use buffered writes and avoid logging very large outputs in full (consider truncation for outputs >1MB).
- **Future enhancements**:
  - Add log analysis CLI tool to parse and visualize logs
  - Add `--log-level` parameter for controlling verbosity
  - Support structured logging to remote endpoints (e.g., log aggregation services)
  - Add summarization of logs at the end of runs
- **Security**: Log files may contain sensitive information from prompts/outputs. Document this and recommend appropriate file permissions.
