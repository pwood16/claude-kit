# Feature: /sonar Command for SonarQube Issue Resolution

## Feature Description
Add a `/sdlc:sonar` command to the SDLC plugin that automatically fetches code quality issues from SonarQube/SonarCloud and iteratively fixes them. The command uses a shell script to query the SonarQube API for issues, then works through them in a loop until all issues are resolved or the user stops the process. This enables developers to maintain high code quality standards with minimal manual effort.

## User Story
As a developer
I want to run a single command that fetches SonarQube issues and fixes them automatically
So that I can maintain code quality without manually reviewing and fixing each issue

## Problem Statement
SonarQube identifies code quality issues, security vulnerabilities, and code smells in codebases. However, developers must manually review the SonarQube dashboard, understand each issue, navigate to the relevant code, and fix it. This process is time-consuming and often gets deprioritized. There's no automated way to fetch SonarQube issues and have Claude fix them in a feedback loop.

## Solution Statement
Create a `/sdlc:sonar` command that:
1. Validates that required environment variables (`SONAR_TOKEN` and `SONAR_URL`) are set, prompting the user to set them if missing
2. Calls a script that queries the SonarQube API for issues in the current project
3. Parses the issues and presents them to Claude for fixing
4. After fixes are applied, re-runs the scan to check for remaining issues
5. Continues the loop until all issues are resolved or the user terminates

## Relevant Files
Use these files to implement the feature:

- `plugins/sdlc/.claude-plugin/plugin.json` - Plugin manifest that needs to be updated with the new command registration
- `plugins/sdlc/README.md` - Documentation to be updated with the new command
- `plugins/sdlc/commands/implement.md` - Reference for command structure and argument handling patterns
- `plugins/sdlc/commands/feature.md` - Reference for command markdown format and frontmatter structure
- `plugins/spawn/scripts/spawn-agent` - Reference for shell script patterns, error handling, and environment variable validation
- `plugins/spawn/commands/wt-agent.md` - Reference for allowed-tools frontmatter and script invocation patterns

### New Files
- `plugins/sdlc/commands/sonar.md` - The main command definition file that orchestrates the sonar workflow
- `plugins/sdlc/scripts/sonar-issues` - Shell script that queries SonarQube API and returns issues in a structured format

## Implementation Plan

### Phase 1: Foundation
- Create the scripts directory structure for the SDLC plugin
- Implement the `sonar-issues` shell script that:
  - Checks for required environment variables (`SONAR_TOKEN`, `SONAR_URL`)
  - Provides clear error messages if variables are missing with instructions on how to set them
  - Queries the SonarQube API for issues using the project key
  - Formats the response in a Claude-readable format (JSON or structured text)
  - Handles API errors gracefully

### Phase 2: Core Implementation
- Create the `sonar.md` command file with:
  - Proper frontmatter (description, allowed-tools, argument-hint)
  - Instructions for parsing arguments (project key, optional filters)
  - Environment variable validation logic
  - Main fix loop orchestration
  - Issue prioritization (critical → major → minor)

### Phase 3: Integration
- Update `plugin.json` to register the new command
- Update `README.md` with documentation for the new command
- Test the command end-to-end with a real SonarQube instance

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create the scripts directory for SDLC plugin
- Create `plugins/sdlc/scripts/` directory
- This follows the pattern established by the spawn plugin

### Step 2: Implement the sonar-issues script
- Create `plugins/sdlc/scripts/sonar-issues` shell script
- Add shebang and script header with usage documentation
- Implement environment variable checking:
  - Check for `SONAR_TOKEN` - if missing, print instructions to set it and exit with error
  - Check for `SONAR_URL` - if missing, print instructions to set it and exit with error
- Accept project key as first argument (required)
- Accept optional filters: `--severities`, `--types`, `--statuses`
- Use `curl` to query SonarQube API endpoint: `${SONAR_URL}/api/issues/search`
- Parse JSON response and format issues for Claude consumption
- Include for each issue: rule, severity, message, component (file path), line number, code snippet context
- Make script executable with `chmod +x`

### Step 3: Create the sonar.md command file
- Create `plugins/sdlc/commands/sonar.md`
- Add frontmatter:
  ```yaml
  ---
  description: Fetch SonarQube issues and fix them in an iterative loop
  allowed-tools:
    - Bash(${CLAUDE_PLUGIN_ROOT}/scripts/sonar-issues:*)
    - Bash(git diff:*)
    - Bash(git status:*)
    - Read
    - Edit
    - Write
    - Grep
    - Glob
    - AskUserQuestion
  argument-hint: <project-key> [--severities BLOCKER,CRITICAL,MAJOR] [--max-iterations N]
  ---
  ```
- Write command instructions that:
  1. Parse `$ARGUMENTS` for project key and optional flags
  2. Check environment variables by running the script with `--check-env` flag
  3. If env vars missing, use AskUserQuestion to prompt user to set them, then exit
  4. Fetch issues using the sonar-issues script
  5. If no issues found, report success and exit
  6. Prioritize issues by severity (BLOCKER > CRITICAL > MAJOR > MINOR > INFO)
  7. For each issue in priority order:
     - Read the affected file
     - Understand the issue and SonarQube rule
     - Apply the fix using Edit tool
     - Track the fix
  8. After fixing a batch, re-run the sonar-issues script to check for remaining issues
  9. Continue until no issues remain or max iterations reached
  10. Report summary of fixes made

### Step 4: Update plugin.json
- No changes needed - Claude Code auto-discovers commands in the commands/ directory

### Step 5: Update README.md
- Add documentation for the `/sdlc:sonar` command
- Include:
  - Command description
  - Required environment variables setup
  - Usage examples
  - Available options

### Step 6: Run Validation Commands
- Execute all validation commands to ensure the feature works correctly

## Testing Strategy

### Unit Tests
- Test sonar-issues script with missing SONAR_TOKEN (should error with helpful message)
- Test sonar-issues script with missing SONAR_URL (should error with helpful message)
- Test sonar-issues script with invalid project key (should error gracefully)
- Test sonar-issues script with valid credentials and project (should return formatted issues)

### Edge Cases
- No issues found in project (should report success)
- SonarQube API is unreachable (should error gracefully)
- Invalid/expired token (should error with re-authentication instructions)
- Very large number of issues (should paginate or limit batch size)
- Issue in file that no longer exists (should skip gracefully)
- Fix introduces new issues (should detect in re-scan)
- Max iterations reached with issues remaining (should report status and exit)

## Acceptance Criteria
- [ ] `/sdlc:sonar <project-key>` command is available and documented
- [ ] Running command without `SONAR_TOKEN` set prompts user with clear setup instructions
- [ ] Running command without `SONAR_URL` set prompts user with clear setup instructions
- [ ] Command successfully fetches issues from SonarQube API
- [ ] Issues are prioritized by severity (BLOCKER first)
- [ ] Claude reads affected files and applies fixes
- [ ] Command re-checks for issues after fixes and continues loop
- [ ] Command terminates when no issues remain
- [ ] Command respects `--max-iterations` flag
- [ ] Summary of fixes is reported at completion
- [ ] README.md is updated with command documentation

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Verify the scripts directory was created
ls -la plugins/sdlc/scripts/

# Verify the sonar-issues script is executable
test -x plugins/sdlc/scripts/sonar-issues && echo "Script is executable" || echo "Script is NOT executable"

# Verify the sonar-issues script has proper shebang
head -1 plugins/sdlc/scripts/sonar-issues | grep -q "#!/" && echo "Has shebang" || echo "Missing shebang"

# Test script behavior with missing env vars (should error gracefully)
unset SONAR_TOKEN SONAR_URL
plugins/sdlc/scripts/sonar-issues test-project 2>&1 | grep -q "SONAR" && echo "Env var check works" || echo "Env var check failed"

# Verify the command file exists and has proper frontmatter
head -20 plugins/sdlc/commands/sonar.md

# Verify README was updated
grep -q "sonar" plugins/sdlc/README.md && echo "README updated" || echo "README not updated"

# Test plugin loads without errors (run from repo root)
claude --plugin-dir plugins/sdlc --help 2>&1 | head -5
```

## Notes
- The SonarQube API uses basic authentication with the token as username and empty password
- API endpoint for issues: `GET /api/issues/search?componentKeys={projectKey}&resolved=false`
- Consider adding support for SonarCloud (different base URL pattern)
- Future enhancement: Add `--branch` flag to check issues on specific branch
- Future enhancement: Add `--auto-commit` flag to commit fixes after each iteration
- The script should handle pagination for projects with many issues (API returns max 500 per page)
- SonarQube rules documentation can be fetched via `/api/rules/show?key={ruleKey}` for better fix context
