---
description: Clean up git worktrees with interactive confirmation
allowed-tools: Bash(git worktree list:*), Bash(git worktree remove:*), Bash(git branch -d:*), Bash(git branch -D:*), Bash(git status:*), Bash(git log:*), Bash(gh pr view:*), Bash(gh pr list:*), AskUserQuestion, Grep
argument-hint: [description-filter]
---

# Clean Git Worktrees

Safely clean up git worktrees with interactive confirmation. Identify stale worktrees (merged PRs, old branches), warn about uncommitted changes, and remove worktrees with optional branch deletion.

## Your Task

### 1. List all worktrees

Run: `git worktree list --porcelain`

Parse the output to extract for each worktree:
- Path (worktree location)
- Branch name (if available)
- Commit SHA and message
- Whether it's detached, locked, or prunable

**Important:** The main repository directory is always listed as a worktree. DO NOT offer to remove it - filter it out from cleanup candidates.

### 2. Filter worktrees (if description provided)

If `$ARGUMENTS` contains a description filter:
- Use AI to intelligently match the description against:
  - Worktree directory names
  - Branch names
  - Recent commit messages
  - Associated PR titles (fetch via `gh pr list --search "head:<BRANCH_NAME>"`)
- Only proceed with worktrees that match the description

If `$ARGUMENTS` is empty:
- Consider all non-main worktrees as candidates for cleanup

### 3. Gather worktree status

For each candidate worktree, gather:

**Basic info:**
- Worktree path
- Branch name
- Last commit message and date

**Staleness indicators:**
- Check if branch is merged into main: `git branch --merged main` (run from main repo)
- Check if associated PR is merged/closed: `gh pr list --search "head:<BRANCH_NAME>" --json state,number,title`
- Check last commit age: `git log -1 --format=%cr <COMMIT_SHA>`

**Uncommitted changes:**
- Navigate to worktree: `cd <WORKTREE_PATH>`
- Check status: `git status --porcelain`
- If there are uncommitted changes, capture file list

### 4. Present worktrees for confirmation

For each worktree, show a clear summary:
```
Worktree: /path/to/repo/feature-name
Branch: feature-name
Last commit: "Add feature X" (2 weeks ago)
Status: [MERGED/STALE/ACTIVE]
⚠️  Uncommitted changes: 3 files modified
Associated PR: #123 (merged)
```

Use `AskUserQuestion` to present options for each worktree:
- "Remove worktree only" → Remove worktree, keep branch
- "Remove worktree and delete branch" → Remove worktree and branch (use `-d` if merged, `-D` if not)
- "Skip this worktree" → Keep it
- If uncommitted changes exist, add warning in question text

### 5. Execute removal

For each worktree the user chose to remove:

**Remove the worktree:**
- First try: `git worktree remove <WORKTREE_PATH>`
- If it fails due to uncommitted changes:
  - Use `AskUserQuestion` to ask:
    - "Force remove (lose uncommitted changes)" → `git worktree remove --force <WORKTREE_PATH>`
    - "Cancel removal" → Skip this worktree

**Delete branch (if user selected):**
- Check if branch is merged: `git branch --list <BRANCH_NAME> --merged main`
- If merged: `git branch -d <BRANCH_NAME>` (safe delete)
- If not merged: `git branch -D <BRANCH_NAME>` (force delete)
- If branch deletion fails, report error but continue

### 6. Provide summary

After processing all worktrees, show:
- Number of worktrees removed
- Number of branches deleted
- Any errors or warnings
- List of remaining worktrees (if any)

## Examples

### Clean all stale worktrees
```
/gh:wt-clean
```
Lists all worktrees and prompts for each one.

### Clean worktrees matching description
```
/gh:wt-clean authentication feature
```
Finds worktrees related to authentication and prompts to remove them.

### Clean merged PR worktrees
```
/gh:wt-clean merged PRs
```
AI matches against merged PR status and old branches.

## Security Note

**What this command can do:**
- List git worktrees
- Check worktree status and uncommitted changes
- Remove worktrees (with confirmation)
- Delete local branches (with confirmation)
- Read PR information to determine staleness

**What it cannot do:**
- Delete the main repository directory
- Force remove without user confirmation
- Delete remote branches
- Push changes to remote
- Modify uncommitted work without explicit user permission

**Safety features:**
- Interactive confirmation before any removal
- Warns about uncommitted changes
- Separate confirmation for force removal
- Uses safe branch deletion (`-d`) when possible
- Never removes the main worktree
