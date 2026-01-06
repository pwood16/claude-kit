---
description: Run multi-agent PR review in background (architecture, quality, edge cases)
allowed-tools: Bash(git branch:*), Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh pr checks:*), Bash(mkdir -p /tmp/pr-review:*), Bash(uuidgen:*), Bash(wc -c < /tmp/pr-review:*), Bash(tr:*), Bash(echo:*), Write(path:/tmp/pr-review/**), Task
argument-hint: [pr-number-or-branch]
---

# Multi-Agent PR Review

Launch a 5-step background review pipeline for a pull request.

## Your Task

### 1. Determine the PR to review

**Argument handling:**
- If `$ARGUMENTS` is empty: use current branch to find associated PR
- If `$ARGUMENTS` is a number (e.g., "123"): treat as PR number directly
- If `$ARGUMENTS` is not a number: treat as branch name and find its PR

To find PR from current branch:
```bash
gh pr view --json number,title,body,author,url,baseRefName,headRefName,createdAt,commits,reviews,comments
```

To find PR by number:
```bash
gh pr view $ARGUMENTS --json number,title,body,author,url,baseRefName,headRefName,createdAt,commits,reviews,comments
```

To find PR by branch:
```bash
gh pr list --head "$ARGUMENTS" --json number --jq '.[0].number'
```

### 2. Gather PR context

Once you have the PR number, collect all necessary context:

```bash
# Get PR metadata
gh pr view $PR_NUMBER --json number,title,body,author,url,baseRefName,headRefName,createdAt,commits,reviews,comments

# Get PR diff
gh pr diff $PR_NUMBER

# Get CI/CD check status
gh pr checks $PR_NUMBER --json name,state
```

Also get the list of changed files from the diff output.

### 3. Create work directory

Generate a unique session ID and create the work directory:

```bash
session_id=$(uuidgen | tr '[:upper:]' '[:lower:]')
work_dir="/tmp/pr-review/$session_id"
mkdir -p "$work_dir"
```

### 4. Write context.json

Create the context file with ALL gathered information. This must include:

```json
{
  "pr": {
    "number": <number>,
    "title": "<title>",
    "body": "<description>",
    "author": "<author login>",
    "url": "<PR URL>",
    "base_branch": "<base ref>",
    "head_branch": "<head ref>",
    "created_at": "<timestamp>"
  },
  "commits": [
    {
      "sha": "<commit sha>",
      "message": "<commit message>",
      "author": "<author>",
      "date": "<timestamp>"
    }
  ],
  "diff": "<full diff content>",
  "files_changed": ["file1.ts", "file2.ts"],
  "checks": {
    "status": "passing|failing|pending",
    "details": [
      {"name": "<check name>", "status": "<success|failure|pending>"}
    ]
  },
  "reviews": [
    {
      "author": "<reviewer>",
      "state": "<APPROVED|CHANGES_REQUESTED|COMMENTED>",
      "body": "<review comment>"
    }
  ],
  "comments": [],
  "repo_path": "<absolute path to repository>"
}
```

The `repo_path` should be the current working directory (the repository root).

Write this to `$work_dir/context.json`.

### 5. Check context size

Before spawning the orchestrator, check the context.json size:
```bash
wc -c < "$work_dir/context.json"
```

If it exceeds 500KB (512000 bytes), warn the user that the PR may be too large for effective review but proceed anyway.

### 6. Spawn background review task

Use the **Task tool** with `run_in_background: true` to launch the review pipeline:

```
Task tool parameters:
- subagent_type: "gh:pr-review-launcher"
- run_in_background: true
- prompt: "Run the PR review orchestrator. work_dir: {work_dir}, repo_path: {repo_path}"
- description: "PR review #{pr_number}"
```

This spawns a background agent that will run the orchestrator shell script. The agent will show up in `/tasks` and can be monitored.

### 7. Report to user

Output a summary showing:

```
Starting multi-agent PR review for PR #<number>...

PR: <title> (#<number>)
Author: <author>
Files changed: <count>

Review session: <session_id>
Work directory: <work_dir>

5-step review pipeline:
  1. Architecture & Standards
  2. Code Quality - Pass 1 (Initial)
  3. Code Quality - Pass 2 (Validate/Challenge)
  4. Code Quality - Pass 3 (Synthesize)
  5. Edge Cases & Final Summary

Check status:  cat <work_dir>/status.json
Monitor task:  /tasks
Final review:  <work_dir>/3-final-summary.md
```

## Error Handling

- If no PR is found for the branch, inform the user
- If gh CLI fails, report the error
- If context gathering fails, stop and report which step failed

## Note

This command spawns the review as a **background task** and returns immediately. The review pipeline may take several minutes to complete.

**To monitor progress:**
- Use `/tasks` to see the background task status
- Check `status.json` in the work directory for step-by-step progress
- The final review will be in `3-final-summary.md`
