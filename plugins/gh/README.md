# GitHub Workflow Plugin

GitHub branch and PR workflow commands for Claude Code.

## Commands

### `/gh:load-pr [branch-or-pr-number]`

Fetch, checkout, and load PR context for review.

**Usage:**
```bash
/gh:load-pr               # Use current branch
/gh:load-pr 123           # Checkout PR #123's branch
/gh:load-pr feature-auth  # Checkout feature-auth branch
```

**What it does:**
1. Determines target branch (from PR number or branch name)
2. Checks for uncommitted changes (prompts to stash if needed)
3. Fetches and checks out the branch
4. Loads PR details, diff, and CI status
5. Summarizes what needs review

**Permissions:**
- Fetch and checkout branches (local git operations)
- Stash uncommitted changes (with confirmation)
- Read PR information via GitHub CLI
- **Cannot**: push, commit, merge, or modify PRs

### `/gh:wt-list [description-filter]`

List all git worktrees with their status and PR information.

**Usage:**
```bash
/gh:wt-list              # List all worktrees
/gh:wt-list auth         # Filter worktrees matching "auth"
/gh:wt-list "bug fix"    # Filter worktrees related to bug fixes
```

**What it shows:**
- Worktree name and branch
- Git status (clean/uncommitted/ahead/behind)
- Associated PR number, title, and state
- Last commit message
- Full path to worktree

**What it does:**
1. Lists all git worktrees in the repository
2. For each worktree, gathers:
   - Working tree status (clean/uncommitted)
   - Upstream tracking (ahead/behind counts)
   - Last commit information
   - Associated PR details from GitHub
3. Optionally filters using AI to match description against worktree names, branches, commits, and PR titles
4. Displays formatted output with color-coded status
5. Shows summary statistics (total count, uncommitted, unpushed, open PRs)

**Permissions:**
- Read git worktree list
- Check git status in worktrees (read-only)
- Query GitHub for PR information (read-only)
- **Cannot**: create, modify, or remove worktrees

## Installation

Part of claude-kit marketplace:

```bash
# Install from claude-kit repo
claude --plugin-dir /path/to/claude-kit/plugins/gh
```

## Requirements

- Git repository
- GitHub CLI (`gh`) installed and authenticated
- Internet connection for GitHub API
