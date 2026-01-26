---
description: Spawn a new Claude agent in a git worktree for parallel development
allowed-tools:
  - Bash(git rev-parse:*)
  - Bash(${CLAUDE_PLUGIN_ROOT}/scripts/spawn-agent:*)
  - AskUserQuestion
argument-hint: <worktree-name> [prompt]
---

# Spawn Agent Command

Spawn a new Claude agent in a git worktree for parallel development work.

## Your Task

### 1. Parse Arguments

The `$ARGUMENTS` variable contains: `<worktree-name> [optional prompt text]`

Examples:
- `feature-login` → worktree_name="feature-login", prompt=(default)
- `feature-login Add login form` → worktree_name="feature-login", prompt="Add login form"

**Parsing:**
- First word is always the worktree name
- Everything after the first word is the prompt (if provided)
- If only worktree name provided, let the script use its default prompt

### 2. Validate Environment

- Check we're in a git repository: `git rev-parse --git-dir`
- If not in git repo, show error: "Error: Not in a git repository. The /spawn command requires a git repository to create worktrees."

### 3. Invoke spawn-agent Script

Call the bundled script with the parsed arguments:
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/spawn-agent "$worktree_name" "$prompt"
```

**If prompt is empty:**
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/spawn-agent "$worktree_name"
```

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
- That a new dark blue Alacritty window has been spawned
- Window title: "Claude: <repo-name>/<worktree-name>"
- The new agent is working in isolation with the provided prompt

## Usage Examples

**User invocation:**
```
/spawn:wt-agent feature-login
/spawn:wt-agent feature-login Add user login form with email/password
/spawn:wt-agent bugfix-auth Fix authentication token expiration issue
```

**Agent invocation (when user asks for parallel work):**

When user says things like:
- "Let's work on the login feature in a separate agent"
- "Can you spawn an agent to handle the tests?"
- "Create a new worktree for this bugfix"
- "Spawn an agent with the prompt from instructions.md"

The agent should:
1. Determine appropriate worktree name (e.g., feature-login, test-suite, bugfix-auth)
2. Formulate clear prompt for the spawned agent
   - If user references a file, read it first using the Read tool
   - Then pass the file contents as the prompt argument
3. Use the Skill tool to invoke the slash command:
   ```
   Skill tool with skill: "spawn:wt-agent", args: "<worktree-name> <prompt>"
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
