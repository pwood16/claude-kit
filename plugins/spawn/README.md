# Spawn Plugin

Spawn new Claude agents in git worktrees for parallel development.

## Description

The `spawn` plugin provides a `/spawn:wt-agent` command that creates isolated git worktrees and launches new Claude instances to work on tasks in parallel. Each spawned agent runs in a distinctive Alacritty terminal window with color-coded backgrounds to identify the mode (dark blue for interactive/print, purple for ralph).

Worktrees are created in the `.wt-agents/` directory at the repository root. This directory is gitignored by default, preventing accidental commits of worktree files.

## Prerequisites

- Git repository (must be run from within a repo)
- Ghostty or Alacritty terminal emulator
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

### Ralph mode (spec-driven autonomous development)
```
/spawn:wt-agent feature-api --mode ralph --prd specs/api-feature.json --max-iterations 20
```

Ralph mode spawns an autonomous agent that works through a structured PRD/spec file, implementing stories in priority order (P0, then P1, then P2). The agent iteratively completes each story, updates the spec, and logs progress.

**Key features:**
- Requires `--prd FILE` pointing to a PRD/spec JSON file with structured stories
- PRD file is copied to the worktree and a progress file (`<prd-name>-progress.txt`) is created
- Each iteration spawns a fresh `claude -p` process (bash while loop)
- Agent reads stories from PRD, selects highest-priority unblocked story, implements it, marks complete
- Respects `blocked_by` dependencies between stories
- Automatically commits changes after each iteration
- Runs until all stories are complete or max iterations reached
- Terminal has **purple background** (#2e1a4a) and **[Ralph]** title indicator for easy identification
- No user interaction during iterations

**Required option:**
- `--prd FILE`: Path to PRD/spec JSON file. Stories must have fields: `id`, `title`, `priority` (P0/P1/P2), `status`, `blocked_by` (array of story IDs)

**Optional parameters:**
- `--max-iterations N`: Stop after N iterations (default: 0 = unlimited)
- `--completion-promise TEXT`: Stop when TEXT appears in agent output (default: "TASK COMPLETE")

**PRD file format example:**
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

**Use cases:**
- Spec-driven development: Work through structured PRDs with multiple stories
- Feature implementation: Complete stories in priority order with dependency tracking
- Iterative progress tracking: Agent logs learnings and progress after each story

**Example commands:**
```
# Implement API feature spec with iteration limit
/spawn:wt-agent feature-api --mode ralph --prd specs/api-feature.json --max-iterations 20

# Work through refactoring spec
/spawn:wt-agent refactor-auth --mode ralph --prd specs/auth-refactor.json --max-iterations 10

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

1. Creates git worktree at `<repo-root>/.wt-agents/<worktree-name>`
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

# Spec-driven development with PRD (ralph mode)
/spawn:wt-agent feature-api --mode ralph --prd specs/api-feature.json --max-iterations 20

# Refactoring spec implementation (ralph mode)
/spawn:wt-agent refactor-auth --mode ralph --prd specs/auth-refactor.json --max-iterations 10

# Greenfield PRD with default completion promise (ralph mode)
/spawn:wt-agent greenfield-app --mode ralph --prd prd.json
```
