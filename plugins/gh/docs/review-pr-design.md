# Multi-Agent PR Review Command

> **Design Document** for `claude-kit/plugins/gh`
>
> For fresh-eyes review before implementation

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

## Key Constraint

From [Subagents docs](https://code.claude.com/docs/en/sub-agents):
> "Subagents cannot spawn other subagents"

**Solution**: Use CLI orchestration via `claude --print --agent` from a bash script. This spawns separate CLI processes rather than subagent-to-subagent calls within Claude.

## User Requirements

- **Execution**: Asynchronous (background via `nohup`)
- **Storage**: `/tmp/pr-review/{session-id}/`
- **Model**: Sonnet for all agents
- **Integration**: New command `/gh:review-pr` (not modifying existing `load-pr`)
- **Future-proof**: Design for git worktree support without blocking changes

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

### 2. `hooks-handlers/review-pr-orchestrator.sh`

> **Docs**: [CLI Reference](https://code.claude.com/docs/en/cli-reference) - `--print`, `--agent`, `--model` flags

**Key CLI flags** (from docs):
- `claude -p` / `--print`: Execute without interactive mode, return response
- `--agent <name>`: Specify agent for the session
- `--model <alias>`: Set model (`sonnet`, `opus`, `haiku`)

Pattern from `capture-session.sh`:
```bash
#!/bin/bash
set -e

work_dir="$1"
repo_path="$2"  # Explicit repo path for worktree compatibility

# Status tracking (5 steps total: arch, quality x3, finalizer)
update_status() { ... }

# Agent 1: Architecture
update_status "in_progress" 1
agent1_output=$(cat "$work_dir/context.json" | claude --print \
  --agent pr-architecture-reviewer \
  --model sonnet \
  'Review this PR for architecture compliance:')
echo "$agent1_output" > "$work_dir/1-architecture.md"

# Agent 2: Quality Pass 1 - Initial review
update_status "in_progress" 2
quality1_output=$(cat "$work_dir/context.json" "$work_dir/1-architecture.md" | claude --print \
  --agent pr-quality-reviewer \
  --model sonnet \
  'Initial code quality review, building on architecture findings:')
echo "$quality1_output" > "$work_dir/2-quality-pass1.md"

# Agent 2: Quality Pass 2 - Validate and challenge
update_status "in_progress" 3
quality2_output=$(cat "$work_dir/context.json" "$work_dir/2-quality-pass1.md" | claude --print \
  --agent pr-quality-reviewer \
  --model sonnet \
  'Review the previous quality assessment. Validate findings, challenge assumptions, add anything missed:')
echo "$quality2_output" > "$work_dir/2-quality-pass2.md"

# Agent 2: Quality Pass 3 - Synthesize
update_status "in_progress" 4
quality3_output=$(cat "$work_dir/context.json" "$work_dir/2-quality-pass1.md" "$work_dir/2-quality-pass2.md" | claude --print \
  --agent pr-quality-reviewer \
  --model sonnet \
  'Synthesize the two quality passes into a final quality assessment:')
echo "$quality3_output" > "$work_dir/2-quality-final.md"

# Agent 3: Finalizer (includes all previous)
update_status "in_progress" 5
final_output=$(cat "$work_dir/context.json" "$work_dir/1-architecture.md" "$work_dir/2-quality-final.md" | claude --print \
  --agent pr-summary-finalizer \
  --model sonnet \
  'Create final summary with edge case analysis:')
echo "$final_output" > "$work_dir/3-final-summary.md"

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

Each agent follows `session-summarizer.md` pattern:

```yaml
---
name: pr-architecture-reviewer
description: Reviews PRs for architecture and standards compliance
model: sonnet
---

[System prompt with general guidelines - agent applies judgment based on PR context]
```

**Agent 1 (Architecture)**: Architecture patterns, standards compliance, dependencies, file organization
- General guidelines approach (not detailed checklists)
- Let agent apply judgment based on PR context

**Agent 2 (Quality)**: Code quality, error handling, testing, security, documentation
- **Runs 3 times** for iterative refinement:
  - Pass 1: Initial quality review
  - Pass 2: Validates/challenges Pass 1 findings, adds missed items
  - Pass 3: Synthesizes into final quality assessment
- General guidelines approach
- Builds on Agent 1's findings, avoids duplication

**Agent 3 (Finalizer)**: Edge cases, synthesis of all reviews, verdict (APPROVE/REQUEST_CHANGES), prioritized action items
- Consolidates previous reviews
- Catches what others missed
- Produces actionable final summary

### 4. Output Files

```
/tmp/pr-review/{session-id}/
├── context.json           # PR metadata + diff + repo_path
├── status.json            # Progress tracking (step 1-5)
├── 1-architecture.md      # Agent 1 output
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
8. Test the full pipeline
