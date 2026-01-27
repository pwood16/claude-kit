---
description: Spawn a new Claude agent in a git worktree for parallel development
allowed-tools:
  - Bash(git rev-parse:*)
  - Bash(${CLAUDE_PLUGIN_ROOT}/scripts/spawn-agent:*)
  - AskUserQuestion
argument-hint: <worktree-name> [prompt] [--mode interactive|print]
---

# Spawn Agent Command

Spawn a new Claude agent in a git worktree for parallel development work.

## Your Task

### 1. Parse Arguments

The `$ARGUMENTS` variable contains: `<worktree-name> [optional prompt text] [--mode interactive|print]`

Examples:
- `feature-login` → worktree_name="feature-login", prompt=(default), mode=interactive
- `feature-login Add login form` → worktree_name="feature-login", prompt="Add login form", mode=interactive
- `research-task Explore options --mode print` → worktree_name="research-task", prompt="Explore options", mode=print

**Parsing:**
- First word is always the worktree name
- Look for `--mode interactive` or `--mode print` flag (default: interactive if not specified)
- Everything else (excluding --mode flag) is the prompt
- If only worktree name provided, let the script use its default prompt

**Modes:**
- `interactive` (default): Agent stays in REPL after initial prompt, terminal stays open for follow-up questions
  - User can press Ctrl+O to see thinking
  - User can use /rename to name the session
  - User can use /resume later to continue
- `print`: Agent completes the initial prompt and exits, terminal auto-closes
  - Useful for one-shot tasks where no interaction is needed
  - Terminal disappears when work is complete

### 2. Validate Environment

- Check we're in a git repository: `git rev-parse --git-dir`
- If not in git repo, show error: "Error: Not in a git repository. The /spawn command requires a git repository to create worktrees."

### 3. Invoke spawn-agent Script

Call the bundled script with the parsed arguments:

**With mode specified:**
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/spawn-agent "$worktree_name" "$prompt" --mode "$mode"
```

**With prompt but default mode (interactive):**
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/spawn-agent "$worktree_name" "$prompt"
```

**With just worktree name:**
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/spawn-agent "$worktree_name"
```

**Important:** Pass the full prompt text (everything that isn't the worktree name or --mode flag) to the script. The script will handle it properly.

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
- Mode (interactive or print)
- That a new dark blue terminal window has been spawned
- Window title: "Claude: <repo-name>/<worktree-name>"
- The new agent is working in isolation with the provided prompt
- If interactive mode: remind them they can use Ctrl+O to see thinking, /rename to name the session
- If print mode: remind them the terminal will auto-close when complete

## Usage Examples

**User invocation:**
```
/spawn:wt-agent feature-login
/spawn:wt-agent feature-login Add user login form with email/password
/spawn:wt-agent bugfix-auth Fix authentication token expiration issue
/spawn:wt-agent research-task Explore alternative approaches --mode print
/spawn:wt-agent feature-api Build REST API --mode interactive
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
4. Use the Skill tool to invoke the slash command:
   ```
   # Interactive mode (default)
   Skill tool with skill: "spawn:wt-agent", args: "<worktree-name> <prompt>"

   # Print mode (auto-close when done)
   Skill tool with skill: "spawn:wt-agent", args: "<worktree-name> <prompt> --mode print"
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
