---
description: Fetch SonarQube issues and fix them in an iterative loop
allowed-tools:
  - Bash(uv run ${CLAUDE_PLUGIN_ROOT}/scripts/sonar-issues.py:*)
  - Bash(git diff:*)
  - Bash(git status:*)
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - AskUserQuestion
argument-hint: <project-key> [--severities BLOCKER,CRITICAL,MAJOR] [--branch BRANCH] [--max-iterations N]
---

# SonarQube Issue Resolution

Fetch code quality issues from SonarQube/SonarCloud and fix them iteratively.

## Your Task

### 1. Parse Arguments

The `$ARGUMENTS` variable contains: `<project-key> [--severities BLOCKER,CRITICAL,MAJOR,MINOR,INFO] [--branch BRANCH] [--max-iterations N]`

Examples:
- `my-project` → project_key="my-project", severities=(all), branch=(auto-detect), max_iterations=10
- `my-project --severities BLOCKER,CRITICAL` → project_key="my-project", severities="BLOCKER,CRITICAL", branch=(auto-detect), max_iterations=10
- `my-project --branch main` → project_key="my-project", severities=(all), branch="main", max_iterations=10
- `my-project --max-iterations 5` → project_key="my-project", severities=(all), branch=(auto-detect), max_iterations=5
- `org:my-project --severities CRITICAL,MAJOR --max-iterations 20` → project_key="org:my-project", severities="CRITICAL,MAJOR", branch=(auto-detect), max_iterations=20

**Parsing:**
- First word (or first word with colon like `org:project`) is the project key
- Look for `--severities` flag with comma-separated values
- Look for `--branch` flag to specify branch (default: auto-detect current git branch)
- Look for `--max-iterations` flag (default: 10)

If project key not found you can likely find it in the repositories sonar-project.properties file

**Note:** By default, the command auto-detects the current git branch and checks issues on that branch. Use `--branch` to override.

### 2. Validate Environment

First, check that the required environment variables are configured:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/sonar-issues.py --check-env
```

**Note:** This command requires [uv](https://docs.astral.sh/uv/) to be installed. Install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`

If this command fails (non-zero exit code), the script will display instructions for setting up `SONAR_TOKEN` and `SONAR_URL`. In this case:

1. Use AskUserQuestion to inform the user that environment variables need to be configured
2. Provide the setup instructions from the script output
3. Ask if they want to configure them now or exit
4. If they exit, stop the command gracefully

### 3. Fetch Issues

Run the sonar-issues script to fetch current issues:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/sonar-issues.py "$project_key" [--severities "$severities"] [--branch "$branch"]
```

The script auto-detects the current git branch by default and queries SonarQube for issues on that branch. Use `--branch` to override.

Parse the output to understand:
- Total number of issues
- Issues grouped by severity (BLOCKER > CRITICAL > MAJOR > MINOR > INFO)
- Each issue's details: file, line, message, rule

If no issues are found, report success and exit.

### 4. Fix Issues Iteratively

Work through issues in priority order:

**Priority Order:**
1. BLOCKER - Must fix, breaks the build or critical functionality
2. CRITICAL - Serious issues that could cause bugs or security vulnerabilities
3. MAJOR - Important code quality issues
4. MINOR - Less important issues
5. INFO - Informational suggestions

**For each issue:**

1. **Read the affected file** using the Read tool
2. **Understand the issue:**
   - What SonarQube rule was violated?
   - What is the specific problem in the code?
   - What is the recommended fix?
3. **Apply the fix** using the Edit tool
   - Make minimal, targeted changes
   - Don't refactor beyond what's needed to fix the issue
   - Preserve existing code style and formatting
4. **Track progress** - Note which issues have been fixed

**Batch size:** Fix up to 10 issues per iteration before re-checking.

### 5. Re-check and Continue Loop

After fixing a batch of issues:

1. Run the sonar-issues script again to check for remaining issues
2. Compare with previous count to verify fixes were effective
3. If new issues were introduced, address those first
4. Continue until:
   - No issues remain (success!)
   - Max iterations reached
   - User stops the process

**Important:** Some fixes may introduce new issues (e.g., fixing one code smell might create another). Be aware of this and adjust fixes if needed.

### 6. Report Summary

When complete (or when stopping), provide a summary:

- Total issues fixed
- Issues remaining (if any)
- Files modified
- Iterations completed
- Breakdown by severity

Example:
```
## SonarQube Resolution Summary

**Project:** my-project
**Iterations:** 3 of 10 max

### Issues Resolved
- BLOCKER: 2
- CRITICAL: 5
- MAJOR: 12

### Issues Remaining
- MINOR: 3
- INFO: 8

### Files Modified
- src/auth/login.ts
- src/utils/helpers.ts
- src/api/client.ts

All blocking and critical issues have been resolved!
```

## Error Handling

**API Errors:**
- 401 Unauthorized: Token is invalid or expired - prompt user to regenerate
- 403 Forbidden: No access to project - check project key and permissions
- 404 Not Found: Project doesn't exist - verify project key

**File Errors:**
- If a file mentioned in an issue doesn't exist locally, skip that issue and note it
- If a file can't be edited (permissions), report the issue and continue

**Fix Errors:**
- If a fix can't be applied cleanly, skip and note it
- Don't force changes that don't make sense in context

## Security Note

**What this command can do:**
- Read files in the current repository
- Edit files to fix code quality issues
- Query the SonarQube API (read-only)

**What it cannot do:**
- Push changes to remote
- Modify SonarQube configuration
- Access files outside the repository
- Execute arbitrary code from SonarQube responses
