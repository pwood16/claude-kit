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

### `/gh:pr-draft`

Smart commit, push, and create draft PR with AI-generated description.

**Usage:**
```bash
/gh:pr-draft              # From any branch
```

**What it does:**
1. Analyzes unstaged changes and unpushed commits
2. Creates feature branch if on `main` (pattern: `feature/{description}`)
3. Intelligently stages related files (prompts about unclear files)
4. Commits with auto-generated message
5. Pushes to remote
6. Creates draft PR with AI-generated description including:
   - Summary focusing on the "why"
   - Testing instructions
   - Mermaid diagrams when complexity warrants
   - Succinct, professional tone

**Permissions:**
- Stage, commit, and push changes
- Create branches
- Create draft PRs
- **Cannot**: merge, force push, or modify existing commits

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
