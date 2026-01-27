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

### Basic usage (interactive mode, default)
```
/spawn:wt-agent feature-login
```

Creates a worktree named `feature-login` and spawns an interactive Claude agent. After completing the initial task, the agent stays in REPL mode so you can continue the conversation.

### With custom prompt
```
/spawn:wt-agent feature-login Add user login form with email and password authentication
```

Creates the worktree and gives the agent specific instructions.

### Print mode (auto-close when done)
```
/spawn:wt-agent research-task Explore alternative approaches --mode print
```

Spawns an agent that completes the task and exits. The terminal window automatically closes when done. Useful for:
- Spawning multiple agents for parallel research
- One-shot tasks where no interaction is needed
- Batch operations

### Interactive mode (explicit)
```
/spawn:wt-agent feature-api Build REST API endpoints --mode interactive
```

Explicitly set interactive mode. After completing the initial prompt, the agent stays open for follow-up questions. You can:
- Press **Ctrl+O** to toggle thinking visibility
- Use **/rename** to name the session
- Use **/resume** later to continue the conversation

### Using a file as the prompt

Ask Claude to read the file and spawn the agent:
```
User: "Spawn an agent in worktree 'feature-login' with the prompt from instructions.md"
Claude: [Reads instructions.md, then uses Skill tool with the file contents]
```

This is useful for complex, multi-line prompts stored in files.

### Agent invocation

When you ask your agent to work on something in parallel:
```
User: "Let's add user authentication in a separate agent"
Agent: [Uses Skill tool with skill: "spawn:wt-agent", args: "feature-auth Add user authentication system"]

User: "Spawn 5 agents to research different approaches, have them close when done"
Agent: [Uses Skill tool with --mode print for each agent]
```

## What Happens

When you run `/spawn:wt-agent <worktree-name> [prompt] [--mode interactive|print]`:

1. Creates git worktree at `<repo-root>/<worktree-name>`
2. Generates prompt file at `.agent-prompts/<worktree-name>.md`
3. Spawns new Alacritty window with:
   - Title: `Claude: <repo-name>/<worktree-name>`
   - Size: 120×20 (compact)
   - Background: Dark blue (#1a1a2e) for easy identification
4. Launches Claude in the worktree with your prompt
5. Behavior depends on mode:
   - **Interactive mode** (default): Agent completes the initial prompt, then stays in REPL mode for continued conversation. Terminal stays open.
   - **Print mode**: Agent completes the initial prompt and exits. Terminal automatically closes when done.

## Identifying Spawned Agents

Spawned agents appear in dark blue Alacritty windows, making them easy to distinguish from your main terminal.

## Error Handling

- **Not in git repo**: Shows friendly error message
- **Script not found**: Provides installation instructions
- **Worktree exists**: Script reuses existing worktree
- **Worktree creation fails**: Shows git error

## Examples

```bash
# Simple feature work (interactive mode, default)
/spawn:wt-agent feature-dashboard

# Bug fix with context (interactive, can ask follow-ups)
/spawn:wt-agent bugfix-auth Fix token expiration issue in auth middleware

# Testing work (interactive)
/spawn:wt-agent test-suite Add integration tests for API endpoints

# Refactoring (interactive)
/spawn:wt-agent refactor-components Extract shared components from pages

# Research task (print mode, auto-closes when done)
/spawn:wt-agent research-options Investigate caching strategies --mode print

# Parallel research (spawn multiple in print mode)
/spawn:wt-agent research-alpha Explore approach A --mode print
/spawn:wt-agent research-beta Explore approach B --mode print
/spawn:wt-agent research-gamma Explore approach C --mode print
```
