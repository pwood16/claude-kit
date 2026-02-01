# Spawn Plugin

Spawn new Claude agents in git worktrees for parallel development.

## Description

The `spawn` plugin provides a `/spawn:wt-agent` command that creates isolated git worktrees and launches new Claude instances to work on tasks in parallel. Each spawned agent runs in a distinctive Alacritty terminal window with color-coded backgrounds to identify the mode (dark blue for interactive/print, purple for ralph).

## Prerequisites

- Git repository (must be run from within a repo)
- Ghostty or Alacritty terminal emulator
- Claude Code CLI
- [uv](https://docs.astral.sh/uv/) (for ralph-loop script)

**Note:** The spawn-agent script is bundled with the plugin, no separate installation needed. The ralph-loop script is implemented in Python and uses uv for dependency management.

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

### Ralph mode (spec-driven autonomous development)
```
/spawn:wt-agent feature-api --mode ralph --prd specs/api-feature.json --max-iterations 20
```

Ralph mode spawns an autonomous agent that works through a structured spec file, implementing tasks/stories iteratively. The agent completes each task, updates the spec, and logs progress.

**Key features:**
- Requires `--prd FILE` (or `--spec FILE`) pointing to a spec file
- Supports two spec formats: **Markdown** and **JSON** (see formats below)
- Spec file is copied to the worktree and a progress file (`<spec-name>-progress.txt`) is created
- Each iteration spawns a fresh `claude -p` process
- Agent reads tasks from spec, implements the next incomplete one, marks it complete
- Automatically commits changes after each iteration
- Runs until all tasks are complete or max iterations reached
- Terminal has **purple background** (#2e1a4a) and **[Ralph]** title indicator for easy identification
- No user interaction during iterations

**Required option:**
- `--prd FILE` or `--spec FILE`: Path to spec file (Markdown or JSON format)

**Optional parameters:**
- `--max-iterations N`: Stop after N iterations (default: 0 = unlimited)
- `--completion-promise TEXT`: Stop when TEXT appears in agent output (default: "TASK COMPLETE")

#### Markdown Spec Format

Markdown specs use a `## Step by Step Tasks` section with h3 headers as individual tasks. Tasks are executed in order from top to bottom.

```markdown
# Feature: My Feature

## Step by Step Tasks

### Step 1: Create the database schema
- Create migrations for users table
- Add indexes

### Step 2: Implement the API endpoint
- Create route handler
- Add validation

### Step 3: Add tests
- Unit tests for validation
- Integration tests for endpoint
```

When a task is completed, the agent adds `**Status:** complete` after the h3 heading:

```markdown
### Step 1: Create the database schema
**Status:** complete
- Create migrations for users table
- Add indexes
```

#### JSON Spec Format (Legacy)

JSON specs use a `stories` array with priority and dependency tracking.

```json
{
  "name": "Feature Implementation",
  "stories": [
    {
      "id": "story-1",
      "title": "Implement core functionality",
      "priority": "P0",
      "status": "pending",
      "blocked_by": []
    },
    {
      "id": "story-2",
      "title": "Add error handling",
      "priority": "P1",
      "status": "pending",
      "blocked_by": ["story-1"]
    }
  ]
}
```

Stories must have fields: `id`, `title`, `priority` (P0/P1/P2), `status`, `blocked_by` (array of story IDs). Stories are executed in priority order (P0 first, then P1, then P2), respecting `blocked_by` dependencies.

**Use cases:**
- Spec-driven development: Work through structured specs with multiple tasks
- Feature implementation: Complete tasks in order with progress tracking
- Iterative progress tracking: Agent logs learnings and progress after each task
- Integration with SDLC plugin: `feature-loop` uses `ralph-loop` internally with Markdown specs

**Example commands:**
```
# Implement Markdown feature spec
/spawn:wt-agent feature-api --mode ralph --spec specs/issue-my-feature.md --max-iterations 20

# Implement JSON PRD with iteration limit
/spawn:wt-agent feature-api --mode ralph --prd specs/api-feature.json --max-iterations 20

# Work through refactoring spec
/spawn:wt-agent refactor-auth --mode ralph --spec specs/auth-refactor.md --max-iterations 10

# Greenfield project with PRD (uses default "TASK COMPLETE" promise)
/spawn:wt-agent greenfield-app --mode ralph --prd prd.json
```

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

When you run `/spawn:wt-agent <worktree-name> [prompt] [--mode interactive|print|ralph] [--prd FILE] [options]`:

1. Creates git worktree at `<repo-root>/<worktree-name>`
2. Generates prompt file at `.agent-prompts/<worktree-name>.md`
3. Spawns new Alacritty window with:
   - Title: `Claude: <repo-name>/<worktree-name>` (or `Claude [Ralph]: ...` for ralph mode)
   - Size: 120×20 (compact)
   - Background color varies by mode:
     - **Interactive/Print**: Dark blue (#1a1a2e)
     - **Ralph**: Purple (#2e1a4a)
4. Launches Claude in the worktree with your prompt
5. Behavior depends on mode:
   - **Interactive mode** (default): Agent completes the initial prompt, then stays in REPL mode for continued conversation. Terminal stays open.
   - **Print mode**: Agent completes the initial prompt and exits. Terminal automatically closes when done.
   - **Ralph mode**: Agent works through a PRD/spec file, implementing stories in priority order. Requires `--prd FILE`. PRD and progress file are copied to worktree. Each iteration runs a fresh `claude -p` and commits changes. Stops when all stories are complete or max iterations reached.

## Identifying Spawned Agents

Spawned agents appear in color-coded Alacritty windows:
- **Dark blue** (#1a1a2e): Interactive and print modes
- **Purple** (#2e1a4a) with **[Ralph]** in title: Ralph mode (autonomous iterations)

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

# Spec-driven development with Markdown spec (ralph mode)
/spawn:wt-agent feature-api --mode ralph --spec specs/issue-my-feature.md --max-iterations 20

# Spec-driven development with JSON PRD (ralph mode)
/spawn:wt-agent feature-api --mode ralph --prd specs/api-feature.json --max-iterations 20

# Refactoring spec implementation (ralph mode)
/spawn:wt-agent refactor-auth --mode ralph --spec specs/auth-refactor.md --max-iterations 10

# Greenfield PRD with default completion promise (ralph mode)
/spawn:wt-agent greenfield-app --mode ralph --prd prd.json
```

## Scripts

### `ralph-loop`

The `ralph-loop` script can also be used standalone (outside of `/spawn:wt-agent`) to iterate through a spec file in the current directory.

**Usage:**
```bash
# Run with Markdown spec
./plugins/spawn/scripts/ralph-loop --spec specs/issue-my-feature.md

# Run with JSON PRD
./plugins/spawn/scripts/ralph-loop --prd specs/api-feature.json

# With iteration limit
./plugins/spawn/scripts/ralph-loop --spec specs/feature.md --max-iterations 10

# With custom completion promise
./plugins/spawn/scripts/ralph-loop --spec specs/feature.md --completion-promise "ALL DONE"
```

**Options:**
- `--spec FILE` or `--prd FILE`: Path to spec file (required)
- `--max-iterations N`: Maximum iterations before stopping (default: 0 = unlimited)
- `--completion-promise TEXT`: String that signals completion (default: "TASK COMPLETE")
- `--summary-only`: Show only iteration summaries, suppress verbose Claude output
- `--no-summaries`: Disable iteration summaries (for backwards compatibility)

**How it works:**
1. Validates the spec file format (Markdown or JSON)
2. Creates a progress file (`<spec-name>-progress.txt`) to track learnings
3. Loops: reads spec, finds next incomplete task, runs `claude -p` to implement it
4. Agent updates the spec to mark tasks complete
5. Commits changes after each iteration
6. Exits when all tasks are complete or max iterations reached

**Iteration Summaries:**

After each iteration, `ralph-loop` displays a structured summary showing:
- Iteration number and timestamp
- Task that was worked on (from h3 heading for Markdown, story title for JSON)
- Task completion status (complete/incomplete with color coding)
- Files modified, added, or deleted during the iteration
- Exit status (success/failed)
- Overall progress (X of Y tasks complete)

Example summary output:
```
===================================================================
Iteration 1 Summary - 2026-02-01 08:00:00
===================================================================
Task: Step 1: Create the database schema
Status: complete
Files Modified:
  - migrations/001_create_users.sql
  - migrations/002_add_indexes.sql
Exit Status: Success
Progress: 1 of 3 tasks complete
===================================================================
```

Summaries use color coding for quick visual scanning:
- Green: Success, completed tasks
- Yellow: Incomplete tasks, warnings
- Red: Errors, failures
- Blue: Modified files

Summaries are automatically appended to the progress file (without color codes) for historical reference.

**Summary Control Flags:**

- `--summary-only`: Suppress verbose Claude output, show only iteration summaries. Useful for monitoring progress without full conversation logs.
- `--no-summaries`: Disable iteration summaries entirely for backwards compatibility or when raw output is preferred.

This script is used internally by the SDLC plugin's `feature-loop` to implement feature specs.
