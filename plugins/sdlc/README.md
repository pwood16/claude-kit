# SDLC Plugin

Software development lifecycle automation commands for Claude Code. These commands help you create structured plans for development work and then implement them.

## Commands

### `/sdlc:feature`

Create a comprehensive plan to implement a new feature. Generates a detailed spec with user stories, problem/solution statements, implementation phases, testing strategy, and acceptance criteria. The plan is saved to `specs/issue-{descriptive-name}.md`.

### `/sdlc:bug`

Create a plan to fix a bug. Generates a detailed spec with bug description, steps to reproduce, root cause analysis, and validation commands. The plan is saved to `specs/bug-{descriptive-name}.md`.

### `/sdlc:chore`

Create a plan for maintenance tasks (refactoring, dependency updates, cleanup, etc.). Generates a spec with step-by-step tasks and validation commands. The plan is saved to `specs/issue-{descriptive-name}.md`.

### `/sdlc:implement`

Implement a plan file. Takes a path to a plan file (created by the above commands) as an argument and executes it step by step.

Usage: `/sdlc:implement specs/issue-my-feature.md`

## Installation

Part of claude-kit marketplace:

```bash
# Install from claude-kit repo
claude plugin install sdlc@claude-kit --scope user
```

## Scripts

### `feature-loop`

Automated SDLC workflow that chains together planning, implementation, and iterative code review into a single command.

**What it does:**
1. Creates a feature plan using `/sdlc:feature`
2. Implements the plan using `ralph-loop` (iterative task completion, one task per iteration)
3. Displays implementation summary (iterations, tasks completed, files modified)
4. Runs code review with `acr --local`
5. Displays review findings summary before triage
6. Triages findings (fixes real issues, adds comments for false positives)
7. Repeats review until clean (LGTM) or max iterations reached

**Usage:**
```bash
# Basic usage
./plugins/sdlc/scripts/feature-loop "Add user authentication"

# With options
./plugins/sdlc/scripts/feature-loop --prompt "Add search" --max-review-iterations 3

# Limit implementation iterations
./plugins/sdlc/scripts/feature-loop "Add feature" --max-implement-iterations 10

# Skip review phase (just plan and implement)
./plugins/sdlc/scripts/feature-loop "Quick fix" --skip-review

# Verbose mode
./plugins/sdlc/scripts/feature-loop -v "Add dashboard"
```

**Options:**
- `--prompt`, `-p`: Feature description (alternative to positional arg)
- `--max-implement-iterations`: Maximum ralph-loop iterations for implementation (0=unlimited, default: 0)
- `--max-review-iterations`, `-m`: Maximum review/fix cycles (default: 5)
- `--skip-review`: Skip the review loop
- `--verbose`, `-v`: Enable verbose logging
- `--resume`: Resume from auto-detected checkpoint state
- `--resume-from PATH`: Resume from specific checkpoint state file
- `--no-resume`: Force fresh start, ignore existing checkpoint

**Resuming Failed Runs:**

The `feature-loop` script automatically saves checkpoints after each phase (planning, implementation, review iterations), allowing you to resume from the last successful checkpoint if a failure occurs.

**How it works:**
- After each phase completes successfully, a checkpoint is saved to `.feature-loop-state.json`
- If the process is interrupted (network issues, errors, keyboard interrupt), the checkpoint remains
- Use `--resume` to continue from where you left off
- On successful completion, the checkpoint file is automatically cleaned up

**Resume workflow:**
```bash
# Start a feature loop
./plugins/sdlc/scripts/feature-loop "Add authentication"

# If it fails during implementation or review...
# Resume from the last checkpoint
./plugins/sdlc/scripts/feature-loop --resume

# Or specify a specific checkpoint file
./plugins/sdlc/scripts/feature-loop --resume-from .feature-loop-state.json

# Force a fresh start (ignoring existing checkpoint)
./plugins/sdlc/scripts/feature-loop --no-resume "Add authentication"
```

**What gets skipped when resuming:**
- If checkpoint is in "implementing" phase: skips planning, re-runs implementation and review
- If checkpoint is in "reviewing" phase: skips planning and implementation, continues review from saved iteration

**Checkpoint file format:**
The checkpoint file (`.feature-loop-state.json`) contains:
- Feature prompt and plan file path
- Current phase and review iteration number
- Configuration snapshot (for validation on resume)
- Timestamps for tracking

**Troubleshooting:**
- If checkpoint is corrupted: use `--no-resume` to start fresh
- If plan file is missing: restore it or start fresh
- If checkpoint is from old version: warnings will be shown, consider fresh start
- Multiple features: each run uses the same checkpoint file, so complete or `--no-resume` before starting another

**Requirements:**
- `claude` CLI in PATH
- `acr` CLI in PATH (unless using `--skip-review`)
- `uv` for running the Python script
- `spawn` plugin installed (provides `ralph-loop` script)

**Configuration:**

The `feature-loop` script supports configuration files to set default behavior without passing command-line arguments every time. Configuration files are named `.claude-kit` and use JSON format.

**Configuration File Locations (in precedence order):**
1. `~/.claude-kit` - User home directory (personal defaults, lowest precedence)
2. `<git-root>/.claude-kit` - Git repository root (project-wide settings)
3. `./.claude-kit` - Current working directory (local overrides, highest precedence)

Command-line arguments always override configuration file values.

**Configuration Format:**

```json
{
  "feature_loop": {
    "max_implement_iterations": 0,
    "max_review_iterations": 5,
    "skip_review": false,
    "verbose": false
  },
  "acr": {
    "num_reviewers": 5
  }
}
```

**Configuration Options:**

- `feature_loop.max_implement_iterations` (integer): Maximum ralph-loop iterations for implementation, 0=unlimited (default: 0)
- `feature_loop.max_review_iterations` (integer): Maximum number of review/fix cycles before stopping (default: 5)
- `feature_loop.skip_review` (boolean): Whether to skip the review phase entirely (default: false)
- `feature_loop.verbose` (boolean): Enable verbose logging output (default: false)
- `acr.num_reviewers` (integer): Number of AI reviewers for code review (default: 5)

**Example Configurations:**

Fast mode (fewer iterations):
```json
{
  "feature_loop": {
    "max_implement_iterations": 5,
    "max_review_iterations": 2,
    "verbose": false
  }
}
```

Thorough mode (more iterations, verbose):
```json
{
  "feature_loop": {
    "max_implement_iterations": 0,
    "max_review_iterations": 10,
    "verbose": true
  }
}
```

Skip reviews by default:
```json
{
  "feature_loop": {
    "skip_review": true
  }
}
```

**Enhanced Observability:**

The `feature-loop` script provides comprehensive visibility into the automated workflow through structured summaries:

**Implementation Summary:**

After the `ralph-loop` implementation phase completes, a summary is displayed showing:
- Total iterations run
- Tasks completed (X of Y)
- Files modified during implementation
- Overall status (ready for review / some tasks incomplete)

Example:
```
===================================================================
Implementation Phase Complete - 2026-02-01 08:15:30
===================================================================
Total Iterations: 5
Tasks Completed: 5 of 5 tasks (100%)
Files Modified:
  - src/auth/login.py
  - src/auth/middleware.py
  - tests/test_auth.py
  - migrations/002_add_users.sql
Status: Ready for review
===================================================================
```

**Code Review Summary:**

After each `acr` review run, a summary is displayed before triage showing:
- Total findings count
- Affected files with finding count per file
- Finding categories (if detected: errors, warnings, security issues)
- LGTM status or indication that fixes are needed

Example (with findings):
```
===================================================================
Code Review Summary - Iteration 1 - 2026-02-01 08:20:15
===================================================================
Total Findings: 3 issues found
Affected Files:
  - src/auth/login.py (2 findings)
  - src/auth/middleware.py (1 finding)
Finding Categories: Security, Error Handling
Status: Issues found - proceeding to triage
===================================================================
```

Example (LGTM):
```
===================================================================
Code Review Summary - Iteration 2 - 2026-02-01 08:25:45
===================================================================
Total Findings: 0 issues
Status: LGTM ✓
===================================================================
```

**Summary Features:**
- Color coding for quick visual scanning (green=success, yellow=warnings, red=errors)
- Concise output (fits on one screen)
- Clear visual boundaries with separator lines
- Summaries are logged to `.feature-loop-{sanitized-prompt}.log` for historical reference
- Integration with `ralph-loop` iteration summaries (see spawn plugin README for details)

**Getting Started:**

Copy the example configuration file to get started:
```bash
cp .claude-kit.example .claude-kit
# Edit .claude-kit to customize your settings
```

**Configuration Validation:**

The script validates configuration values and provides helpful error messages:
- `max_implement_iterations` must be a non-negative integer (0 = unlimited)
- `max_review_iterations` must be a positive integer
- `skip_review` and `verbose` must be boolean values (true/false)
- Invalid JSON will be reported with the error location
- Unknown fields are ignored for forward compatibility

## Development

```bash
# Test locally
claude --plugin-dir /path/to/claude-kit/plugins/sdlc
```
