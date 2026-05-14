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

### `/sdlc:sonar`

Fetch code quality issues from SonarQube/SonarCloud and fix them in an iterative loop. The command queries the SonarQube API for issues, prioritizes them by severity, and works through fixes until all issues are resolved or max iterations is reached.

**By default, the command auto-detects the current git branch** and checks issues on that branch, providing a more relevant developer experience focused on your active work.

**Prerequisites:**

- [uv](https://docs.astral.sh/uv/) - Install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`

**Required Environment Variables:**

```bash
# Your SonarQube/SonarCloud authentication token
export SONAR_TOKEN='your-token-here'

# Base URL of your SonarQube instance
export SONAR_URL='https://sonarcloud.io'  # or your self-hosted URL
```

To generate a token:
1. Go to your SonarQube instance → My Account → Security → Generate Token
2. For SonarCloud: https://sonarcloud.io/account/security

**Usage:**

```bash
# Fix all issues in a project (auto-detects current git branch)
/sdlc:sonar my-project-key

# Fix only blocker and critical issues
/sdlc:sonar my-project-key --severities BLOCKER,CRITICAL

# Explicitly specify a branch (overrides auto-detection)
/sdlc:sonar my-project-key --branch main

# Limit to 5 iterations
/sdlc:sonar my-project-key --max-iterations 5

# Combined options
/sdlc:sonar org:my-project --severities CRITICAL,MAJOR --branch develop --max-iterations 20
```

**Options:**
- `--severities` - Filter by severity: BLOCKER, CRITICAL, MAJOR, MINOR, INFO (comma-separated)
- `--branch` - Branch to check (default: auto-detect current git branch)
- `--max-iterations` - Maximum fix iterations before stopping (default: 10)

**Note:** Branch analysis may require SonarQube Developer Edition or higher for full functionality. Community Edition users may find the branch parameter still works in some versions.

## Installation

Part of claude-kit marketplace:

```bash
# Install from claude-kit repo
claude plugin install sdlc@claude-kit --scope user
```

## Development

```bash
# Test locally
claude --plugin-dir /path/to/claude-kit/plugins/sdlc
```
