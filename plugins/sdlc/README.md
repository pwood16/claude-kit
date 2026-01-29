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

## Development

```bash
# Test locally
claude --plugin-dir /path/to/claude-kit/plugins/sdlc
```
