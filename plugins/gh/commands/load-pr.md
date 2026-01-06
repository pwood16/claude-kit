---
description: Fetch branch, checkout, and load PR context for review
allowed-tools: Bash(git status:*), Bash(git fetch:*), Bash(git checkout:*), Bash(git branch:*), Bash(git log:*), Bash(git stash:*), Bash(gh pr view:*), Bash(gh pr list:*), Bash(gh pr diff:*), Bash(gh pr checks:*), AskUserQuestion, Glob, Read
argument-hint: [branch-name-or-pr-number]
---

# Load PR Context

Fetch and checkout a branch, then load PR context for review.

## Your Task

### 1. Determine target branch

**Argument handling:**
- If $ARGUMENTS is empty: use current branch
- If $ARGUMENTS is a number (e.g., "123"): treat as PR number
  - Run: `gh pr view $ARGUMENTS --json headRefName,number,title`
  - Extract the branch name from `headRefName`
- If $ARGUMENTS is not a number: treat as branch name

### 2. Check for uncommitted changes

Before checkout, check working tree status:
- Run: `git status --porcelain`
- If there are uncommitted changes:
  - Use `AskUserQuestion` to prompt user with options:
    - "Stash changes and continue" → run `git stash push -m "Auto-stash before PR review"`
    - "Abort checkout" → stop here and inform user
    - "Discard changes (dangerous!)" → use `git checkout -f`
  - Wait for user decision before proceeding

### 3. Fetch and checkout branch

- Fetch latest: `git fetch origin`
- Checkout branch: `git checkout <BRANCH_NAME>`
  - If branch doesn't exist locally but exists on remote: `git checkout -b <BRANCH_NAME> origin/<BRANCH_NAME>`
  - If checkout fails, report error to user

### 4. Find associated PR

Once on the branch:
- If we already have PR number from step 1, use it
- Otherwise search: `gh pr list --search "head:<BRANCH_NAME>" --json number,title,url,state`
- If no PR found, inform user (might be a local-only branch)

### 5. Load PR details

If PR exists:
- Full PR info: `gh pr view <PR_NUMBER> --json title,body,commits,reviews,comments,url`
- PR diff: `gh pr diff <PR_NUMBER>`
- Check status: `gh pr checks <PR_NUMBER>`

### 6. Provide context summary

Present:
- Branch name and PR number
- PR title and description
- Number of commits
- Review status and comments
- CI/CD check status
- Key files changed
- Areas needing review attention

Ready to discuss the PR.

## Security Note

**What this command can do:**
- Fetch branches from remote
- Switch branches (checkout)
- Stash uncommitted changes (with user permission)
- Read PR information

**What it cannot do:**
- Create, merge, or close PRs
- Make commits or push changes
- Submit reviews or comments
- Force push or rewrite history
