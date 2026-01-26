# Spawn Plugin

Spawn new Claude agents in git worktrees for parallel development.

## Description

The `spawn` plugin provides a `/spawn:wt-agent` command that creates isolated git worktrees and launches new Claude instances to work on tasks in parallel. Each spawned agent runs in a distinctive dark blue Alacritty terminal window.

## Prerequisites

- Git repository (must be run from within a repo)
- Alacritty terminal emulator
- Claude Code CLI

**Note:** The spawn-agent script is bundled with the plugin, no separate installation needed.

## Usage

### Basic usage (default prompt)
```
/spawn:wt-agent feature-login
```

Creates a worktree named `feature-login` and spawns a Claude agent with default instructions.

### With custom prompt
```
/spawn:wt-agent feature-login Add user login form with email and password authentication
```

Creates the worktree and gives the agent specific instructions.

### Using a file as the prompt
```
/spawn:wt-agent feature-login $(cat instructions.md)
```

Use command substitution to read prompt from a file. This is useful for complex, multi-line prompts.

### Agent invocation

When you ask your agent to work on something in parallel:
```
User: "Let's add user authentication in a separate agent"
Agent: [Uses Skill tool with skill: "spawn:wt-agent", args: "feature-auth Add user authentication system"]
```

## What Happens

When you run `/spawn:wt-agent <worktree-name> [prompt]`:

1. Creates git worktree at `<repo-root>/<worktree-name>`
2. Generates prompt file at `.agent-prompts/<worktree-name>.md`
3. Spawns new Alacritty window with:
   - Title: `Claude: <repo-name>/<worktree-name>`
   - Size: 120×20 (compact)
   - Background: Dark blue (#1a1a2e) for easy identification
4. Launches Claude in the worktree with your prompt

## Identifying Spawned Agents

Spawned agents appear in dark blue Alacritty windows, making them easy to distinguish from your main terminal.

## Error Handling

- **Not in git repo**: Shows friendly error message
- **Script not found**: Provides installation instructions
- **Worktree exists**: Script reuses existing worktree
- **Worktree creation fails**: Shows git error

## Examples

```bash
# Simple feature work
/spawn:wt-agent feature-dashboard

# Bug fix with context
/spawn:wt-agent bugfix-auth Fix token expiration issue in auth middleware

# Testing work
/spawn:wt-agent test-suite Add integration tests for API endpoints

# Refactoring
/spawn:wt-agent refactor-components Extract shared components from pages

# Using a file for complex prompts
/spawn:wt-agent feature-auth $(cat detailed-auth-requirements.md)
```
