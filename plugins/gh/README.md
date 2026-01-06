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
