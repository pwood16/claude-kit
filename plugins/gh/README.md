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

## Skills

### `gh-stack` — stacked pull requests

Auto-triggered skill that teaches the agent to drive GitHub's stacked PRs via the
[`gh stack`](https://github.com/github/gh-stack) CLI extension: when to stack at all, creating a
stack, navigating and editing it, partial merges with automatic rebase and retargeting, and how
merges interact with branch protection and merge queues.

**Provenance:** vendored from the official skill at
[`github/gh-stack/skills/gh-stack`](https://github.com/github/gh-stack/tree/main/skills/gh-stack),
commit `ab00aa4a3f2d` (extension v0.1.0), MIT license (see `skills/gh-stack/LICENSE`). Local
modifications: the frontmatter description reworded to "Use when…" framing plus provenance keys,
a "When to stack" section, one sentence on branch protection under "Merging", a corrected
`add -A`/`-u` note in `references/commands.md` (the CLI opens an editor rather than requiring
`-m`), and a new `references/evals.md`. Everything else is upstream verbatim.

Stacked PRs are in **public preview**, so the command surface can change. To refresh the vendored
copy, diff against upstream `skills/gh-stack/` and re-apply the local modifications listed above.

**Requirements:** `gh extension install github/gh-stack`, and stacked PRs enabled on the target
repository (`gh stack submit` exits 9 when the preview is unavailable there).

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
