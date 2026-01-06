# Multi-Agent PR Review Command

> **Design Document** for `claude-kit/plugins/gh`
>
> For fresh-eyes review before implementation

## Goal

**Produce high-confidence PR reviews through iterative, multi-agent validation - where each pass checks the last before you see the result.**

A single LLM pass can miss things. By combining:
- **Multiple perspectives** (architecture → quality → edge cases)
- **Iterative refinement** (pass 2 challenges pass 1, pass 3 synthesizes)
- **Background execution** (doesn't block your workflow)

...you get a self-validating review that's been checked before it reaches you.

## Overview

Create `/gh:review-pr` - a new command that spawns a 5-step sequential agent pipeline in the background, each step building on the previous analysis via a shared temp directory.

## Documentation References

| Topic | Documentation Link |
|-------|-------------------|
| Subagent Definition | https://code.claude.com/docs/en/sub-agents |
| Slash Commands | https://code.claude.com/docs/en/slash-commands |
| Hooks Reference | https://code.claude.com/docs/en/hooks |
| CLI Reference | https://code.claude.com/docs/en/cli-reference |
| Plugin Creation | https://code.claude.com/docs/en/plugins |
| Plugins Reference | https://code.claude.com/docs/en/plugins-reference |

## Key Constraints

### Subagent Nesting

From [Subagents docs](https://code.claude.com/docs/en/sub-agents):
> "Subagents cannot spawn other subagents"

**Solution**: Use CLI orchestration via `claude --print --agent` from a bash script. This spawns separate CLI processes rather than subagent-to-subagent calls within Claude.

### CLI `--tools` Flag Overrides Agent Configuration

From [CLI Reference](https://code.claude.com/docs/en/cli-reference):
> The `--tools` flag **specifies/restricts** the available tools (overrides defaults)

**Implication**: Do NOT use `--tools` in CLI invocations. Let agent YAML `tools` field be the single source of truth. This:
- Keeps agents self-contained and reusable
- Avoids configuration conflicts
- Simplifies orchestrator script

Same applies to `--model` - let agents define their own model in YAML.

## User Requirements

- **Execution**: Asynchronous (background via `nohup`)
- **Storage**: `/tmp/pr-review/{session-id}/`
- **Model**: Sonnet for all agents (configured in agent YAML, not CLI)
- **Integration**: New command `/gh:review-pr` (not modifying existing `load-pr`)
- **Future-proof**: Design for git worktree support without blocking changes

## Limitations & Best Practices

### PR Size Limits

This tool works best with focused, well-scoped PRs. Large PRs will be rejected:

| Limit | Value | Rationale |
|-------|-------|-----------|
| Context size | 500KB | Prevents context overflow, keeps reviews focused |
| Timeout per agent | 5 minutes | Prevents runaway processes |

**If your PR is too large:**
1. Break it into smaller, logical PRs
2. Use feature flags to ship incrementally
3. Consider a stacked PR workflow

### Best Practices for Reviewable PRs

- **Single responsibility**: One feature/fix per PR
- **~400 lines changed**: Sweet spot for thorough review
- **Clear commit history**: Logical, atomic commits
- **Tests included**: Easier to verify correctness

## Files to Create

```
plugins/gh/
├── agents/
│   ├── pr-architecture-reviewer.md   # Agent 1: Architecture & standards
│   ├── pr-quality-reviewer.md        # Agent 2: Code quality & security
│   └── pr-summary-finalizer.md       # Agent 3: Edge cases & final summary
├── commands/
│   └── review-pr.md                  # Slash command
└── hooks-handlers/
    └── review-pr-orchestrator.sh     # Background orchestrator script
```

## Architecture

```
/gh:review-pr 123
       │
       ▼
┌─────────────────────────────────────────┐
│  review-pr.md (slash command)           │
│  - Gathers PR context via gh CLI        │
│  - Writes context.json to /tmp/...      │
│  - Spawns orchestrator with nohup       │
│  - Returns immediately with paths       │
└─────────────────────────────────────────┘
       │
       ▼ (background)
┌─────────────────────────────────────────┐
│  review-pr-orchestrator.sh              │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │ Agent 1: Architecture           │    │
│  │ Input: context.json             │    │
│  │ Output: 1-architecture.md       │    │
│  └─────────────────────────────────┘    │
│               │                         │
│               ▼                         │
│  ┌─────────────────────────────────┐    │
│  │ Agent 2: Quality (Pass 1)       │    │
│  │ Input: context + arch review    │    │
│  │ Output: 2-quality-pass1.md      │    │
│  └─────────────────────────────────┘    │
│               │                         │
│               ▼                         │
│  ┌─────────────────────────────────┐    │
│  │ Agent 2: Quality (Pass 2)       │    │
│  │ Input: + pass1 findings         │    │
│  │ Output: 2-quality-pass2.md      │    │
│  └─────────────────────────────────┘    │
│               │                         │
│               ▼                         │
│  ┌─────────────────────────────────┐    │
│  │ Agent 2: Quality (Pass 3)       │    │
│  │ Input: + pass1 + pass2          │    │
│  │ Output: 2-quality-final.md      │    │
│  └─────────────────────────────────┘    │
│               │                         │
│               ▼                         │
│  ┌─────────────────────────────────┐    │
│  │ Agent 3: Finalizer              │    │
│  │ Input: context + all reviews    │    │
│  │ Output: 3-final-summary.md      │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

## Future: Git Worktree Support

**Not implementing now, but design ensures compatibility:**

1. **Repo path passed explicitly** - orchestrator receives `$repo_path` arg, doesn't use `pwd`
2. **`context.json` includes `repo_path`** - agents reference files via absolute paths
3. **Session ID format**: `{repo-hash}-{pr-number}-{uuid}` - unique per worktree
4. **No checkout required** - review works on any worktree pointing to the branch

**Future `/gh:review-pr --worktree` could:**
- Create temp worktree: `git worktree add /tmp/pr-worktree-{id} origin/{branch}`
- Run review against that worktree
- Clean up worktree when done
- Enable parallel reviews of multiple PRs

## Implementation Details

### 1. `commands/review-pr.md`

> **Docs**: [Slash Commands](https://code.claude.com/docs/en/slash-commands) - Frontmatter options, argument access

```yaml
---
description: Run multi-agent PR review in background (architecture, quality, edge cases)
allowed-tools: Bash(git branch:*), Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh pr checks:*), Bash(mkdir:*), Bash(cat:*), Bash(uuidgen:*), Bash(nohup:*)
argument-hint: [pr-number-or-branch]
---
```

**Frontmatter fields** (from docs):
- `allowed-tools`: Restricts which tools the command can use
- `argument-hint`: Shows in autocomplete
- `description`: Brief command description

**Argument access** (from docs):
- `$ARGUMENTS`: All arguments as string
- `$1`, `$2`: Positional arguments

**Logic**:
1. Resolve PR from `$ARGUMENTS` (number, branch, or current)
2. Gather context: `gh pr view --json ...`, `gh pr diff`, `gh pr checks`
3. Create work dir: `/tmp/pr-review/{uuid}/`
4. Write `context.json` with all PR data (includes `repo_path` for worktree compat)
5. Spawn orchestrator: `nohup .../review-pr-orchestrator.sh "$work_dir" "$repo_path" </dev/null >/dev/null 2>&1 &`
6. Return paths to user immediately

### context.json Structure

All git information is pre-loaded so agents don't need Bash access:

```json
{
  "pr": {
    "number": 123,
    "title": "Add user authentication",
    "body": "This PR implements OAuth2...",
    "author": "developer",
    "url": "https://github.com/org/repo/pull/123",
    "base_branch": "main",
    "head_branch": "feature/auth",
    "created_at": "2026-01-05T10:00:00Z"
  },
  "commits": [
    {
      "sha": "abc1234",
      "message": "Initial auth implementation",
      "author": "developer",
      "date": "2026-01-05T10:00:00Z"
    },
    {
      "sha": "def5678",
      "message": "Add tests for auth flow",
      "author": "developer",
      "date": "2026-01-05T14:00:00Z"
    }
  ],
  "diff": "diff --git a/src/auth.ts b/src/auth.ts\n...",
  "files_changed": [
    "src/auth/login.ts",
    "src/auth/logout.ts",
    "src/auth/types.ts",
    "tests/auth.test.ts"
  ],
  "checks": {
    "status": "passing",
    "details": [
      {"name": "build", "status": "success"},
      {"name": "test", "status": "success"},
      {"name": "lint", "status": "success"}
    ]
  },
  "reviews": [
    {
      "author": "reviewer1",
      "state": "APPROVED",
      "body": "LGTM"
    }
  ],
  "comments": [],
  "repo_path": "/Users/phil/Dev/repos/project"
}
```

**Key design decisions:**
- `diff`: Full diff content so agents can see exact changes
- `commits`: Commit history with messages for context
- `files_changed`: List enables targeted `Read` calls
- `repo_path`: Absolute path for `Read`/`Grep`/`Glob` operations
- No Bash needed: All git info is already here

### 2. `hooks-handlers/review-pr-orchestrator.sh`

> **Docs**: [CLI Reference](https://code.claude.com/docs/en/cli-reference) - `--print`, `--agent` flags

**Key CLI flags** (from docs):
- `claude -p` / `--print`: Execute without interactive mode, return response
- `--agent <name>`: Specify agent for the session
- `--max-turns <n>`: Limit agentic turns (prevents runaway tool usage)

**Note**: Do NOT use `--tools` or `--model` flags - agents define their own configuration in YAML for reusability.

Pattern from `capture-session.sh`:
```bash
#!/bin/bash
set -e

work_dir="$1"
repo_path="$2"  # Explicit repo path for worktree compatibility

# Per-agent timeout (5 minutes)
AGENT_TIMEOUT=300

# Status tracking (5 steps total: arch, quality x3, finalizer)
update_status() {
  local status="$1"
  local step="$2"
  local error="${3:-null}"
  cat > "$work_dir/status.json" <<EOF
{
  "status": "$status",
  "current_step": $step,
  "total_steps": 5,
  "step_names": ["architecture", "quality-pass1", "quality-pass2", "quality-final", "summary"],
  "updated_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "error": $error
}
EOF
}

# Run agent with timeout and error handling
run_agent() {
  local agent_name="$1"
  local output_file="$2"
  local prompt="$3"
  shift 3
  local input_files=("$@")

  local output
  if output=$(timeout $AGENT_TIMEOUT cat "${input_files[@]}" | claude --print \
    --agent "$agent_name" \
    --max-turns 15 \
    "$prompt" 2>&1); then
    echo "$output" > "$output_file"
    return 0
  else
    local exit_code=$?
    if [ $exit_code -eq 124 ]; then
      echo "Agent timed out after ${AGENT_TIMEOUT}s" > "$output_file.error"
      return 124
    else
      echo "$output" > "$output_file.error"
      return $exit_code
    fi
  fi
}

# Check context size before starting
context_size=$(wc -c < "$work_dir/context.json")
MAX_CONTEXT_SIZE=$((500 * 1024))  # 500KB limit

if [ "$context_size" -gt "$MAX_CONTEXT_SIZE" ]; then
  update_status "failed" 0 '"PR too large for automated review. Context size: '"$context_size"' bytes exceeds limit of '"$MAX_CONTEXT_SIZE"' bytes. Consider breaking into smaller PRs."'
  exit 1
fi

# Agent 1: Architecture
update_status "in_progress" 1
if ! run_agent "gh:pr-architecture-reviewer" "$work_dir/1-architecture.md" \
  'Review this PR for architecture compliance:' \
  "$work_dir/context.json"; then
  update_status "failed" 1 '"Architecture review failed. Check 1-architecture.md.error for details."'
  exit 1
fi

# Agent 2: Quality Pass 1 - Initial review
update_status "in_progress" 2
if ! run_agent "gh:pr-quality-reviewer" "$work_dir/2-quality-pass1.md" \
  'Initial code quality review, building on architecture findings:' \
  "$work_dir/context.json" "$work_dir/1-architecture.md"; then
  update_status "failed" 2 '"Quality pass 1 failed. Check 2-quality-pass1.md.error for details."'
  exit 1
fi

# Agent 2: Quality Pass 2 - Validate and challenge
update_status "in_progress" 3
if ! run_agent "gh:pr-quality-reviewer" "$work_dir/2-quality-pass2.md" \
  'Review the previous quality assessment. Validate findings, challenge assumptions, add anything missed:' \
  "$work_dir/context.json" "$work_dir/2-quality-pass1.md"; then
  update_status "failed" 3 '"Quality pass 2 failed. Check 2-quality-pass2.md.error for details."'
  exit 1
fi

# Agent 2: Quality Pass 3 - Synthesize
update_status "in_progress" 4
if ! run_agent "gh:pr-quality-reviewer" "$work_dir/2-quality-final.md" \
  'Synthesize the two quality passes into a final quality assessment:' \
  "$work_dir/context.json" "$work_dir/2-quality-pass1.md" "$work_dir/2-quality-pass2.md"; then
  update_status "failed" 4 '"Quality synthesis failed. Check 2-quality-final.md.error for details."'
  exit 1
fi

# Agent 3: Finalizer (includes all previous)
update_status "in_progress" 5
if ! run_agent "gh:pr-summary-finalizer" "$work_dir/3-final-summary.md" \
  'Create final summary with edge case analysis:' \
  "$work_dir/context.json" "$work_dir/1-architecture.md" "$work_dir/2-quality-final.md"; then
  update_status "failed" 5 '"Final summary failed. Check 3-final-summary.md.error for details."'
  exit 1
fi

update_status "completed" 5
```

### 3. Agent Definitions

> **Docs**: [Subagents](https://code.claude.com/docs/en/sub-agents) - Definition format, YAML fields

**Agent file format** (from docs):
- Location: `.claude/agents/` (project) or plugin's `agents/` folder
- Format: Markdown with YAML frontmatter

**Required YAML fields**:
- `name`: Unique identifier (lowercase, hyphens)
- `description`: When to invoke this agent

**Optional YAML fields**:
- `model`: `sonnet`, `opus`, `haiku`, or `inherit`
- `tools`: Comma-separated list (omit to inherit all)
- `permissionMode`: `default`, `acceptEdits`, `dontAsk`, etc.

### Tool Permissions (Read-Only Scope)

> **Important**: Tools are specified ONLY in agent YAML. Do not use CLI `--tools` flag (it overrides rather than combines).

**Design Decision: No Bash**

All git information is pre-loaded into `context.json`, eliminating the need for Bash:

```yaml
tools: Read, Grep, Glob
```

| Tool | Purpose | Why Needed |
|------|---------|------------|
| `Read` | Read file contents | Examine specific files mentioned in diff |
| `Grep` | Search for patterns | Find related code, error handling patterns, etc. |
| `Glob` | Find files by pattern | Discover related files, test files, etc. |

**Why no Bash?**
- All git info (commits, diff, history) is pre-loaded in `context.json`
- Eliminates security concerns about destructive commands
- More predictable behavior
- Faster execution (no subprocess spawning)

**CLI invocation (agent controls its own tools/model):**
```bash
claude --print \
  --agent gh:pr-architecture-reviewer \
  --max-turns 15 \
  'Review this PR for architecture compliance:'
```

**`--max-turns 15`**: Limits agentic exploration to prevent runaway tool usage.

### Agent Configurations

> **Namespacing**: Plugin agents can be invoked with or without namespace prefix, but we use `gh:agent-name` for consistency with slash commands and to avoid collisions.

**Agent 1 (Architecture Reviewer)**:
```yaml
---
name: pr-architecture-reviewer
description: Reviews PRs for architecture and standards compliance
model: sonnet
tools: Read, Grep, Glob, Bash(wc:*)
---
```
- Focus: Architecture patterns, standards, dependencies, file organization
- General guidelines approach (not detailed checklists)
- Uses: `Read` to examine file structure, `Grep` to find imports/dependencies
- CLI invocation: `--agent gh:pr-architecture-reviewer`

**Agent 2 (Quality Reviewer)**:
```yaml
---
name: pr-quality-reviewer
description: Reviews PRs for code quality, security, and best practices
model: sonnet
tools: Read, Grep, Glob, Bash(wc:*)
---
```
- Focus: Code quality, error handling, testing, security, documentation
- **Runs 3 times** for iterative refinement:
  - Pass 1: Initial quality review
  - Pass 2: Validates/challenges Pass 1 findings, adds missed items
  - Pass 3: Synthesizes into final quality assessment
- Uses: `Read` to check implementations, `Grep` to find error handling patterns
- CLI invocation: `--agent gh:pr-quality-reviewer`

**Agent 3 (Summary Finalizer)**:
```yaml
---
name: pr-summary-finalizer
description: Synthesizes reviews into final PR assessment with verdict
model: sonnet
tools: Read, Grep, Glob, Bash(wc:*)
---
```
- Focus: Edge cases, synthesis, verdict (APPROVE/REQUEST_CHANGES), action items
- Consolidates previous reviews, catches what others missed
- Uses: `Read` to verify claims, `Glob` to check test coverage
- CLI invocation: `--agent gh:pr-summary-finalizer`

**Adding CLI Utilities to Agents**:

To give agents access to specific CLI tools, use the `Bash(command:*)` syntax in the tools list:
```yaml
tools: Read, Grep, Glob, Bash(wc:*), Bash(head:*), Bash(tail:*)
```

This allows agents to use utilities like `wc -l` for line counts while keeping them restricted from arbitrary shell access.

### 4. Output Files

```
/tmp/pr-review/{session-id}/
├── context.json           # PR metadata + diff + repo_path
├── status.json            # Progress tracking (step 1-5)
├── 1-architecture.md      # Agent 1 output
├── 1-architecture.md.error # (if failed) Error details
├── 2-quality-pass1.md     # Quality Pass 1: Initial review
├── 2-quality-pass2.md     # Quality Pass 2: Validation/challenges
├── 2-quality-final.md     # Quality Pass 3: Synthesized assessment
└── 3-final-summary.md     # Final consolidated review
```

`status.json` format:
```json
{
  "status": "in_progress|completed|failed",
  "current_step": 2,
  "total_steps": 5,
  "step_names": ["architecture", "quality-pass1", "quality-pass2", "quality-final", "summary"],
  "updated_at": "2026-01-06T...",
  "error": null
}
```

**Error states:**
- `"error": null` - No error
- `"error": "Agent timed out after 300s"` - 5-minute timeout exceeded
- `"error": "PR too large for automated review..."` - Context > 500KB

## Command Output

```
Starting multi-agent PR review for PR #123...

PR: Add OAuth2 authentication (#123)
Author: developer
Files changed: 12

Review session: a1b2c3d4-...
Work directory: /tmp/pr-review/a1b2c3d4-.../

5-step review pipeline:
  1. Architecture & Standards
  2. Code Quality - Pass 1 (Initial)
  3. Code Quality - Pass 2 (Validate/Challenge)
  4. Code Quality - Pass 3 (Synthesize)
  5. Edge Cases & Final Summary

Check status:  cat /tmp/pr-review/a1b2c3d4-.../status.json
Final review:  /tmp/pr-review/a1b2c3d4-.../3-final-summary.md
```

## Reference Files

**In-repo patterns to follow:**
- Background agent spawning: `plugins/prior-session/hooks-handlers/capture-session.sh:72-88`
- Agent definition: `plugins/prior-session/agents/session-summarizer.md`
- Command structure: `plugins/gh/commands/load-pr.md`

**Official documentation:**
- [Subagents](https://code.claude.com/docs/en/sub-agents) - Agent definition, YAML fields, invocation
- [Slash Commands](https://code.claude.com/docs/en/slash-commands) - Command format, frontmatter, arguments
- [CLI Reference](https://code.claude.com/docs/en/cli-reference) - `--print`, `--agent`, `--model` flags
- [Hooks Reference](https://code.claude.com/docs/en/hooks) - Hook types, command execution
- [Plugins](https://code.claude.com/docs/en/plugins) - Plugin structure, distribution

## Testing Strategy

### Test 1: Orchestrator Script (Isolated)

Test the orchestrator with mock context before wiring up the full command:

```bash
# Create test directory
mkdir -p /tmp/pr-review/test-001

# Create minimal context.json
cat > /tmp/pr-review/test-001/context.json << 'EOF'
{
  "pr": {
    "number": 999,
    "title": "Test PR",
    "body": "Test description",
    "author": "tester",
    "base_branch": "main",
    "head_branch": "test-branch"
  },
  "commits": [{"sha": "abc123", "message": "Test commit"}],
  "diff": "diff --git a/test.txt b/test.txt\n+hello world",
  "files_changed": ["test.txt"],
  "checks": {"status": "passing"},
  "repo_path": "/Users/phil/Dev/repos/claude-kit"
}
EOF

# Run orchestrator directly (not backgrounded for testing)
./plugins/gh/hooks-handlers/review-pr-orchestrator.sh \
  /tmp/pr-review/test-001 \
  /Users/phil/Dev/repos/claude-kit

# Check outputs
cat /tmp/pr-review/test-001/status.json
cat /tmp/pr-review/test-001/1-architecture.md
cat /tmp/pr-review/test-001/3-final-summary.md
```

**Verify:**
- [ ] status.json shows "completed" with step 5
- [ ] All 6 output files exist (1-architecture, 2-quality-pass1/2/final, 3-final-summary)
- [ ] Agent outputs contain meaningful review content

### Test 2: Tool Access (Verify Read/Grep/Glob work)

```bash
# Test that agents can use tools - add a real file to context
cat > /tmp/pr-review/test-002/context.json << 'EOF'
{
  "pr": {"number": 999, "title": "Test tools", ...},
  "diff": "diff --git a/plugins/gh/README.md ...",
  "files_changed": ["plugins/gh/README.md"],
  "repo_path": "/Users/phil/Dev/repos/claude-kit"
}
EOF
```

**Verify:**
- [ ] Agent output references actual file content (proves Read works)
- [ ] Agent finds related files (proves Glob works)
- [ ] Agent finds patterns (proves Grep works)

### Test 3: Full Command (End-to-End)

Create a test PR or use an existing one:

```bash
# Option A: Use existing PR in another repo
cd /path/to/repo-with-open-pr
/gh:review-pr 123

# Option B: Create test PR in claude-kit
git checkout -b test/pr-review-testing
echo "test" > test-file.txt
git add test-file.txt && git commit -m "Test commit"
git push -u origin test/pr-review-testing
gh pr create --title "Test PR for review command" --body "Testing"

# Run the command
/gh:review-pr
```

**Verify:**
- [ ] Command returns immediately with paths
- [ ] Background process starts (check `ps aux | grep orchestrator`)
- [ ] status.json updates as steps complete
- [ ] Final summary is coherent and references actual PR content

### Test 4: Error Handling

```bash
# Test with invalid context
echo '{"invalid": "json structure"}' > /tmp/pr-review/test-err/context.json
./review-pr-orchestrator.sh /tmp/pr-review/test-err /some/path
```

**Verify:**
- [ ] status.json shows "failed" with error message
- [ ] Partial outputs preserved for debugging
- [ ] Script exits cleanly (no zombie processes)

### Test 5: Large PR (Stress Test)

Find or create a PR with 20+ files changed:

**Verify:**
- [ ] Context.json doesn't exceed reasonable size
- [ ] Agents complete within --max-turns limit
- [ ] Quality passes build on each other (not just repeating)

### Testing Checklist

| Test | Command | Expected Result |
|------|---------|-----------------|
| Orchestrator runs | `./review-pr-orchestrator.sh` | 6 output files created |
| Status tracking | `cat status.json` | Shows step progression |
| Agents use tools | Check output for file refs | References actual code |
| Background exec | `/gh:review-pr` | Returns immediately |
| Error handling | Invalid context | Graceful failure |

### Debug Mode

Add verbose output for debugging:

```bash
# In orchestrator, add debug flag
DEBUG=${DEBUG:-false}
if [ "$DEBUG" = "true" ]; then
  set -x  # Print commands
  exec > >(tee -a "$work_dir/debug.log") 2>&1
fi
```

Run with: `DEBUG=true ./review-pr-orchestrator.sh ...`

## Implementation Order

1. **Save design doc**: Copy this plan to `plugins/gh/docs/review-pr-design.md`
2. Create `plugins/gh/agents/` directory
3. Create 3 agent definition files:
   - `pr-architecture-reviewer.md`
   - `pr-quality-reviewer.md`
   - `pr-summary-finalizer.md`
4. Create `plugins/gh/hooks-handlers/` directory
5. Create `review-pr-orchestrator.sh` (make executable with `chmod +x`)
6. Create `commands/review-pr.md`
7. Update `plugins/gh/README.md` with new command docs
8. **Run Test 1**: Orchestrator with mock context
9. **Run Test 3**: Full end-to-end with real PR
