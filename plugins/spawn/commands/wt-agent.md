---
description: Spawn a new Claude agent in a git worktree for parallel development
allowed-tools:
  - Bash(git rev-parse:*)
  - Bash(${CLAUDE_PLUGIN_ROOT}/scripts/spawn-agent:*)
  - AskUserQuestion
argument-hint: <worktree-name> [prompt] [--mode interactive|print|ralph] [--prd FILE] [--max-iterations N] [--completion-promise TEXT]
---

# Spawn Agent Command

Spawn a new Claude agent in a git worktree for parallel development work.

## Your Task

### 1. Parse Arguments

The `$ARGUMENTS` variable contains: `<worktree-name> [optional prompt text] [--mode interactive|print|ralph] [--prd FILE] [--max-iterations N] [--completion-promise TEXT]`

Examples:
- `feature-login` → worktree_name="feature-login", prompt=(default), mode=interactive
- `feature-login Add login form` → worktree_name="feature-login", prompt="Add login form", mode=interactive
- `research-task Explore options --mode print` → worktree_name="research-task", prompt="Explore options", mode=print
- `feature-api --mode ralph --prd specs/api.json --max-iterations 20` → worktree_name="feature-api", mode=ralph, prd_file="specs/api.json", max_iterations=20
- `refactor-auth --mode ralph --prd prd.json` → worktree_name="refactor-auth", mode=ralph, prd_file="prd.json", completion_promise="TASK COMPLETE" (default)

**Parsing:**
- First word is always the worktree name
- Look for `--mode interactive|print|ralph` flag (default: interactive if not specified)
- Look for `--prd FILE` flag (required for ralph mode, specifies a PRD/spec JSON file)
- Look for `--max-iterations N` flag (only used with ralph mode, default: 0 = unlimited)
- Look for `--completion-promise TEXT` flag (only used with ralph mode, default: "TASK COMPLETE")
- Everything else (excluding flags) is the prompt
- If only worktree name provided, let the script use its default prompt
- When `--prd` is used, the prompt is auto-generated from the PRD structure

**Modes:**
- `interactive` (default): Agent stays in REPL after initial prompt, terminal stays open for follow-up questions
  - User can press Ctrl+O to see thinking
  - User can use /rename to name the session
  - User can use /resume later to continue
- `print`: Agent completes the initial prompt and exits, terminal auto-closes
  - Useful for one-shot tasks where no interaction is needed
  - Terminal disappears when work is complete
- `ralph`: Autonomous agent runs a bash loop, spawning fresh `claude -p` for each iteration
  - Each iteration is a new Claude process that sees previous work in files and git history
  - Automatically commits changes after each iteration
  - Runs until all PRD stories are complete or max iterations reached
  - Terminal has purple background (#2e1a4a) and [Ralph] title indicator for easy identification
  - **Required option:**
    - `--prd FILE`: Path to PRD/spec JSON file. File is copied to the worktree and a structured prompt is generated that instructs the agent to work through stories in priority order (P0, then P1, then P2). Stories must have: `id`, `title`, `priority`, `status`, `blocked_by` fields. A progress file (`<prd-name>-progress.txt`) is created to track learnings across iterations.
  - **Optional parameters:**
    - `--max-iterations N`: Stop after N iterations (default: 0 = unlimited)
    - `--completion-promise TEXT`: Stop when TEXT appears in agent output (default: "TASK COMPLETE")
  - Use for: spec-driven development, PRD implementation, structured feature work

### 2. Validate Environment

- Check we're in a git repository: `git rev-parse --git-dir`
- If not in git repo, show error: "Error: Not in a git repository. The /spawn command requires a git repository to create worktrees."

### 3. Invoke spawn-agent Script

Call the bundled script with the parsed arguments:

**With mode specified:**
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/spawn-agent "$worktree_name" "$prompt" --mode "$mode"
```

**With ralph mode and PRD:**
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/spawn-agent "$worktree_name" --mode ralph --prd "$prd_file" --max-iterations 20
```

**With prompt but default mode (interactive):**
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/spawn-agent "$worktree_name" "$prompt"
```

**With just worktree name:**
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/spawn-agent "$worktree_name"
```

**Important:** Pass the full prompt text (everything that isn't the worktree name or flags) to the script. The script will handle it properly.

### 4. Handle Errors

If the script fails (non-zero exit):
- Display the script's error output (script already has good error messages)
- Common errors the script handles:
  - Not in a git repository
  - Worktree creation failure
  - Alacritty not available

### 5. Confirm Success

When successful, inform the user:
- Worktree name
- Mode (interactive, print, or ralph)
- Terminal appearance:
  - Interactive/print modes: dark blue terminal with title "Claude: <repo-name>/<worktree-name>"
  - Ralph mode: purple terminal (#2e1a4a) with title "Claude [Ralph]: <repo-name>/<worktree-name>"
- The new agent is working in isolation with the provided prompt
- If interactive mode: remind them they can use Ctrl+O to see thinking, /rename to name the session
- If print mode: remind them the terminal will auto-close when complete
- If ralph mode: remind them the agent will iterate automatically, check the terminal output for progress

## Usage Examples

**User invocation:**
```
/spawn:wt-agent feature-login
/spawn:wt-agent feature-login Add user login form with email/password
/spawn:wt-agent bugfix-auth Fix authentication token expiration issue
/spawn:wt-agent research-task Explore alternative approaches --mode print
/spawn:wt-agent feature-api Build REST API --mode interactive
/spawn:wt-agent feature-api --mode ralph --prd specs/api-feature.json --max-iterations 20
/spawn:wt-agent refactor-auth --mode ralph --prd specs/auth-refactor.json --max-iterations 10
/spawn:wt-agent greenfield-app --mode ralph --prd prd.json
```

**Agent invocation (when user asks for parallel work):**

When user says things like:
- "Let's work on the login feature in a separate agent"
- "Can you spawn an agent to handle the tests?"
- "Create a new worktree for this bugfix"
- "Spawn an agent with the prompt from instructions.md"
- "Spawn 5 agents to research different approaches"

The agent should:
1. Determine appropriate worktree name (e.g., feature-login, test-suite, bugfix-auth)
2. Formulate clear prompt for the spawned agent
   - If user references a file, read it first using the Read tool
   - Then pass the file contents as the prompt argument
3. **Decide on mode based on user intent:**
   - Use `--mode interactive` (or omit for default) when:
     - User wants to interact with the agent after initial work
     - Building features that may need follow-up
     - Debugging or exploring where back-and-forth is expected
   - Use `--mode print` when:
     - Spawning multiple agents for parallel research (e.g., 5 agents exploring options)
     - One-shot tasks with clear deliverables
     - Batch operations where no interaction is needed
     - User wants terminals to auto-close when done
   - Use `--mode ralph` when:
     - User wants autonomous iterative development without interaction
     - User has a PRD/spec JSON file with structured stories to implement
     - Task benefits from working through stories in priority order (P0, P1, P2)
     - User mentions "implement this spec" or "work through this PRD"
     - Task requires tracking progress across multiple iterations
     - User wants to set iteration limits or completion conditions
4. Use the Skill tool to invoke the slash command:
   ```
   # Interactive mode (default)
   Skill tool with skill: "spawn:wt-agent", args: "<worktree-name> <prompt>"

   # Print mode (auto-close when done)
   Skill tool with skill: "spawn:wt-agent", args: "<worktree-name> <prompt> --mode print"

   # Ralph mode with PRD (spec-driven development)
   Skill tool with skill: "spawn:wt-agent", args: "<worktree-name> --mode ralph --prd specs/feature.json --max-iterations 20"
   Skill tool with skill: "spawn:wt-agent", args: "<worktree-name> --mode ralph --prd prd.json"
   ```

## Security Note

**What this command can do:**
- Create git worktrees in the current repository
- Spawn new Alacritty terminal windows
- Launch Claude instances with specific prompts

**What it cannot do:**
- Modify the main branch or existing branches
- Push to remote
- Delete worktrees or branches
- Access files outside the repository
