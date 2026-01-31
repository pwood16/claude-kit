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
3. Runs code review with `acr --local`
4. Triages findings (fixes real issues, adds comments for false positives)
5. Repeats review until clean (LGTM) or max iterations reached

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
