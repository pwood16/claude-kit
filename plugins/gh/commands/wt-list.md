---
description: List all git worktrees with status and PR information
allowed-tools: Bash(git worktree:*), Bash(git -C:*), Bash(git status:*), Bash(git log:*), Bash(git rev-list:*), Bash(gh pr list:*), Bash(gh pr view:*), Glob, Read, Grep
argument-hint: [description-filter]
---

# List Git Worktrees

List all git worktrees with their status, branch information, PR details, and last commit.

## Your Task

### 1. Get worktree list

Run: `git worktree list --porcelain`

Parse the output to extract:
- Worktree path
- Branch name
- HEAD commit SHA

**Format of porcelain output:**
```
worktree /path/to/worktree
HEAD <sha>
branch refs/heads/<branch-name>

worktree /path/to/another
HEAD <sha>
branch refs/heads/<another-branch>
```

### 2. For each worktree, gather information

For each worktree path, collect:

**a) Git status:**
- Run in worktree: `git -C <worktree-path> status --porcelain`
- Classify as:
  - "clean" if no output
  - "uncommitted" if has output

**b) Upstream tracking:**
- Run: `git -C <worktree-path> rev-list --left-right --count HEAD...@{upstream} 2>/dev/null`
- Output format: `<ahead>\t<behind>`
- If command fails (no upstream), mark as "no upstream"
- Otherwise parse ahead/behind counts

**c) Last commit:**
- Run: `git -C <worktree-path> log -1 --format="%h %s" HEAD`
- Extract short SHA and subject

**d) Associated PR (if branch is not main/master):**
- Run: `gh pr list --search "head:<branch-name>" --json number,title,state --limit 1`
- If found, extract PR number, title, and state

### 3. Optional filtering with AI

If $ARGUMENTS is provided (description filter):
- Collect all worktree data first
- Use AI reasoning to match the description against:
  - Worktree directory name
  - Branch name
  - Last commit message
  - PR title (if exists)
- Show only worktrees that intelligently match the description
- Use fuzzy/semantic matching (e.g., "auth" matches "authentication", "login", "user-auth")

### 4. Display formatted output

For each worktree, display:

```
<worktree-name> (<branch-name>)
  Status: <clean|uncommitted> [↑N ahead] [↓N behind] [⚠ no upstream]
  PR: #<number> - <title> (<state>)  [or "No PR" if none]
  Last: <short-sha> <commit-message>
  Path: <full-path>
```

**Color coding (use ANSI):**
- 🟢 Green: Clean working tree, no unpushed commits
- 🟡 Yellow: Staged/untracked/unpushed changes
- 🔴 Red: Uncommitted changes present

**Sorting:**
- Show main worktree first (the repository root)
- Then sort by worktree name alphabetically

**Example output:**
```
claude-kit (main)
  Status: clean
  PR: No PR
  Last: b28c629 feat(sdlc): add SDLC plugin
  Path: /Users/phil/Dev/repos/claude-kit

feature-auth (feature-auth-system)
  Status: uncommitted, ↑2 ahead
  PR: #42 - Add user authentication system (open)
  Last: 8a3b2c1 Add login form validation
  Path: /Users/phil/Dev/repos/claude-kit/feature-auth

bugfix-api (bugfix-api-error)
  Status: clean, ↑1 ahead
  PR: #38 - Fix API error handling (open)
  Last: f7e9d4a Handle timeout errors properly
  Path: /Users/phil/Dev/repos/claude-kit/bugfix-api
```

### 5. Summary statistics

After listing all worktrees, show:
- Total worktrees count
- Count with uncommitted changes
- Count with unpushed commits
- Count with open PRs

## Security Note

**What this command can do:**
- List git worktrees (read-only)
- Check git status in worktrees (read-only)
- Query GitHub for PR information (read-only)
- Read commit history (read-only)

**What it cannot do:**
- Create, modify, or remove worktrees
- Make commits or push changes
- Modify PRs or branches
- Execute arbitrary commands outside git/gh
