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

### `/gh:wt-clean [description]`

Clean up git worktrees with interactive confirmation.

**Usage:**
```bash
/gh:wt-clean                    # List all worktrees for cleanup
/gh:wt-clean authentication     # Clean worktrees matching "authentication"
/gh:wt-clean merged PRs         # Clean worktrees with merged PRs
```

**What it does:**
1. Lists all git worktrees (excluding main repository)
2. Filters by description if provided (AI matches against names, branches, commits, PRs)
3. Checks staleness (merged PRs, old commits, branch status)
4. Warns about uncommitted changes
5. Prompts for removal with options (worktree only or worktree + branch)
6. Safely removes selected worktrees and branches

**Permissions:**
- List and inspect worktrees
- Remove worktrees (with confirmation)
- Delete local branches (with confirmation)
- Read PR information to determine staleness
- **Cannot**: delete main worktree, delete remote branches, or force remove without permission

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
