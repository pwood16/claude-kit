# Cleared Sessions Tracker - Plan

**Status**: Planning Phase
**Goal**: Make it easy to find and reference conversations after running `/clear`

## Problem Statement

When you run `/clear` in Claude Code:
- A new session starts with a fresh context window
- The old session's JSONL transcript is preserved in `~/.claude/projects/`
- But the old session is hard to discover - it's just a UUID filename
- No easy way to answer "what did I discuss about authentication last week?"

## Solution Overview

Create a lightweight plugin that:
1. **Captures metadata** when `/clear` is run (via hook)
2. **Generates a summary** of the cleared session (via subagent)
3. **Stores session metadata** alongside the transcript for easy discovery
4. **Provides a `/prior-sessions` command** to browse cleared sessions

## Architecture

### Plugin Structure

```
claude-kit/
├── .claude-plugin/
│   └── plugin.json                    # Plugin metadata
├── hooks/
│   └── hooks.json                     # Hook configuration
├── hooks-handlers/
│   └── on-clear.sh                    # Triggered when /clear runs
├── agents/
│   └── session-summarizer.md         # Subagent for summarization
├── commands/
│   └── prior-sessions.md              # Slash command to browse sessions
└── scripts/
    └── statusline.sh                  # Existing statusline script
```

### Data Flow

```
User runs /clear
    ↓
UserPromptSubmit hook fires
    ↓
on-clear.sh hook script runs
    ├─→ Extracts session metadata (session_id, transcript_path, cwd, etc.)
    ├─→ Parses JSONL for basic info (first message, files touched, duration)
    ├─→ Spawns session-summarizer subagent in background
    └─→ Writes initial metadata to <session_id>.cleared.json
         ↓
session-summarizer subagent
    ├─→ Reads the full JSONL transcript
    ├─→ Generates concise summary (2-3 sentences)
    └─→ Updates <session_id>.cleared.json with summary
         ↓
User later runs /prior-sessions
    ↓
Claude reads all *.cleared.json files
    ↓
Displays formatted list of cleared sessions
```

## Storage Design

### Location
Store metadata files alongside transcripts in the project directory:

```
~/.claude/projects/-Users-phil-Dev-repos-claude-kit/
├── 636bbf12-b19c-4cce-ae7c-d75133c7bfee.jsonl          # Original transcript
├── 636bbf12-b19c-4cce-ae7c-d75133c7bfee.cleared.json   # Our metadata ← NEW
└── 2e2f2c54-d0b2-4253-9adc-dcd45d46c1f4.jsonl          # New session after /clear
```

### Benefits of This Structure
- **Co-located**: Metadata next to transcript it describes
- **Easy to glob**: `find ~/.claude/projects -name "*.cleared.json"` finds all cleared sessions
- **Per-project**: Matches Claude's organization pattern
- **Self-contained**: Deleting a project cleans up its metadata too

### Metadata File Format

**File**: `<session_id>.cleared.json`

```json
{
  "version": "1.0",
  "session_id": "636bbf12-b19c-4cce-ae7c-d75133c7bfee",
  "cleared_at": "2026-01-03T00:30:15Z",
  "project": {
    "name": "claude-kit",
    "path": "/Users/phil/Dev/repos/claude-kit",
    "git_branch": "session-tracker"
  },
  "transcript": {
    "path": "/Users/phil/.claude/projects/-Users-phil-Dev-repos-claude-kit/636bbf12...jsonl",
    "message_count": 122,
    "duration_minutes": 135,
    "started_at": "2026-01-02T18:26:19Z"
  },
  "content": {
    "first_message": "Please take a look at the markdown file and lets brainstorm on this feature a bit...",
    "files_touched": [
      "statusline.sh",
      "README.md",
      "scripts/README.md",
      ".gitignore"
    ],
    "title": "Enhanced statusline with git status",
    "summary": "Built enhanced statusline showing git status indicators (+staged, !modified, ?untracked, ↑unpushed, ⚠no-upstream). Restructured documentation into main README linking to scripts/README for detailed instructions. Added upstream tracking detection to warn when remote branch is missing."
  }
}
```

## Hook Implementation

### hooks/hooks.json

Uses the **SessionEnd** hook which fires when a Claude Code session ends, including when `/clear` is called.

**References:**
- [SessionEnd Hook Documentation](https://code.claude.com/docs/en/hooks#sessionend)
- [Hooks Guide](https://code.claude.com/docs/en/hooks-guide)

```json
{
  "description": "Track cleared sessions for easy reference",
  "hooks": {
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks-handlers/on-clear.sh"
          }
        ]
      }
    ]
  }
}
```

**When it fires:**
- User closes terminal
- User runs `/clear` (with `reason: "clear"`)
- User logs out (with `reason: "logout"`)

**Hook input (via stdin):**
```json
{
  "session_id": "636bbf12-b19c-4cce-ae7c-d75133c7bfee",
  "transcript_path": "/Users/phil/.claude/projects/-Users-phil-Dev-repos-claude-kit/636bbf12...jsonl",
  "cwd": "/Users/phil/Dev/repos/claude-kit",
  "permission_mode": "default",
  "hook_event_name": "SessionEnd",
  "reason": "clear"
}
```

### hooks-handlers/on-clear.sh

**Responsibilities**:
1. Extract session metadata from hook input (stdin JSON)
2. Parse JSONL transcript for basic info (fast operations only)
3. Invoke `session-summarizer` agent to generate title + summary
4. Write complete `.cleared.json` file with summary

**Implementation**:
```bash
#!/bin/bash
set -e

# Read hook input from SessionEnd
input=$(cat)
session_id=$(echo "$input" | jq -r '.session_id')
transcript_path=$(echo "$input" | jq -r '.transcript_path')
cwd=$(echo "$input" | jq -r '.cwd')
reason=$(echo "$input" | jq -r '.reason')

# Only process if this was a /clear (not a normal exit)
[ "$reason" != "clear" ] && exit 0

# Exit if transcript doesn't exist
[ ! -f "$transcript_path" ] || exit 0

# Extract basic metadata from JSONL (fast operations)
first_message=$(jq -s '[.[] | select(.type == "user")][0].message.content // ""' "$transcript_path")
message_count=$(jq -s '[.[] | select(.type == "user")] | length' "$transcript_path")

# Get git info
git_branch=$(git branch --show-current 2>/dev/null || echo "")
git_repo=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" || basename "$cwd")

# Calculate duration (first to last message timestamp)
started_at=$(jq -s '.[0].timestamp // ""' "$transcript_path")
cleared_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Invoke session-summarizer agent to get title + summary
# Agent reads the transcript and returns structured JSON
summary_json=$(claude --print \
  --agent session-summarizer \
  --output-format json \
  --json-schema '{"type":"object","properties":{"title":{"type":"string"},"summary":{"type":"string"}},"required":["title","summary"]}' \
  "Summarize the session transcript at: $transcript_path" 2>/dev/null || echo '{"title":"","summary":""}')

title=$(echo "$summary_json" | jq -r '.title // ""')
summary=$(echo "$summary_json" | jq -r '.summary // ""')

# Extract files touched (Write and Edit tool uses)
files_touched=$(jq -s '[
  .[] |
  select(.type == "assistant") |
  .message.content[]? |
  select(.type == "tool_use") |
  select(.name == "Write" or .name == "Edit") |
  .input.file_path
] | unique' "$transcript_path")

# Write complete metadata file
cleared_json_path="${transcript_path%.jsonl}.cleared.json"
cat > "$cleared_json_path" <<EOF
{
  "version": "1.0",
  "session_id": "$session_id",
  "cleared_at": "$cleared_at",
  "project": {
    "name": "$git_repo",
    "path": "$cwd",
    "git_branch": "$git_branch"
  },
  "transcript": {
    "path": "$transcript_path",
    "message_count": $message_count,
    "started_at": "$started_at"
  },
  "content": {
    "first_message": "$first_message",
    "files_touched": $files_touched,
    "title": "$title",
    "summary": "$summary"
  }
}
EOF

exit 0
```

**Key Points**:
- Uses `claude --print --agent` to invoke summarizer
- Agent runs synchronously (hook waits for result)
- Structured JSON output with schema validation
- Fails gracefully (empty title/summary if agent fails)
- Only processes `reason: "clear"` (not normal exits)

## Subagent Design

### agents/session-summarizer.md

Agent for generating concise summaries of cleared sessions.

**References:**
- [Sub-agents Documentation](https://code.claude.com/docs/en/sub-agents)
- [CLI Reference](https://code.claude.com/docs/en/cli-reference)

```markdown
---
name: session-summarizer
description: Generates title and summary for cleared Claude Code sessions
model: haiku
tools: Read, Grep
---

You are a session summarizer for Claude Code. Your task is to analyze conversation transcripts and generate concise summaries.

## Your Task

When given a transcript path, you will:

1. **Read the transcript** using the Read tool
2. **Analyze the conversation**:
   - What was the user trying to accomplish?
   - What did you help them build, fix, or understand?
   - What files were modified?
   - What was the final state when the session was cleared?

3. **Generate structured output** with TWO fields:
   - **title** (5-8 words): A scannable label for quick identification
   - **summary** (2-3 sentences): Key accomplishments and outcomes

## Output Format

Always output valid JSON in this exact format:

```json
{
  "title": "Enhanced statusline with git status",
  "summary": "Built enhanced statusline showing git status indicators (+staged, !modified, ?untracked, ↑unpushed, ⚠no-upstream). Restructured documentation into main README linking to scripts/README for detailed instructions. Added upstream tracking detection to warn when remote branch is missing."
}
```

## Guidelines

- **Be factual**: Focus on what was actually accomplished, not intentions
- **Be concise**: Title should be 5-8 words, summary 2-3 sentences
- **Be specific**: Mention concrete outcomes (files created, bugs fixed, features added)
- **Avoid fluff**: No phrases like "successfully completed" or "helped the user"

## Example Input

User asks: "Summarize the session transcript at: /Users/phil/.claude/projects/.../636bbf12.jsonl"

## Example Output

```json
{
  "title": "Fixed OAuth token refresh bug",
  "summary": "Debugged and fixed OAuth token refresh bug in auth.ts. Added error handling for expired tokens and edge case testing. Updated type definitions to support new error states."
}
```
```

**How It's Invoked** (from hook):
```bash
claude --print \
  --agent session-summarizer \
  --output-format json \
  --json-schema '{"type":"object","properties":{"title":{"type":"string"},"summary":{"type":"string"}},"required":["title","summary"]}' \
  "Summarize the session transcript at: $transcript_path"
```

**Configuration Benefits:**
- Uses **haiku** model for speed and cost efficiency
- Has access to **Read** and **Grep** tools only (no Write/Edit needed)
- Agent prompt can be iterated independently of hook script
- Model can be changed in agent definition (haiku → sonnet if needed)

## Slash Command

### commands/prior-sessions.md

```markdown
Show my prior cleared sessions from this project (or all projects if I ask).

Read from *.cleared.json files in the ~/.claude/projects/ directories and display:

- **Date cleared** (human-friendly format)
- **Title** (the quick scannable title)
- **Summary** (expandable detail - show abbreviated by default)
- **Files touched** (count and key files)
- **Session ID** (first 8 chars for reference)

**Format** as a clean, scannable list:

```
Recent Cleared Sessions (claude-kit)
═════════════════════════════════════

[Jan 2, 2026 8:30pm] Enhanced statusline with git status (636bbf12)
  → Built enhanced statusline showing git status indicators (+staged, !modified,
    ?untracked, ↑unpushed, ⚠no-upstream). Restructured documentation into main
    README linking to scripts/README. Added upstream tracking detection.
  📝 4 files: statusline.sh, README.md, scripts/README.md, .gitignore

[Jan 1, 2026 3:15pm] Fixed OAuth token refresh bug (a7f3e891)
  → Fixed OAuth token refresh bug, added error handling for expired tokens,
    updated tests to cover edge cases.
  📝 3 files: auth.ts, auth.test.ts, types.ts

...
```

**Default**: Show last 10 sessions from current project, most recent first.

**If I provide a search term**, filter sessions by:
- Summary content
- First message content
- Files touched

**If I ask for "all projects"**, search across all ~/.claude/projects/ directories.

**If I ask to "show more"**, display the next batch of sessions.
```

## Configuration (Future)

Store plugin config in `.claude/settings.json` (or plugin-specific config):

```json
{
  "plugins": {
    "claude-kit": {
      "cleared_sessions": {
        "enabled": true,
        "scope": "all",              // "all" | "current-project"
        "default_limit": 10,
        "summarization": {
          "enabled": true,
          "model": "sonnet",         // Which model for summarization
          "max_tokens": 150
        }
      }
    }
  }
}
```

**For MVP**: Hardcode sensible defaults, add configuration later.

## Implementation Phases

### Phase 1: Basic Metadata Capture (MVP)
- ✅ Define plugin structure
- ⬜ Create `on-clear.sh` hook script
  - Extract session metadata
  - Parse basic info from JSONL
  - Write `.cleared.json` file
- ⬜ Test hook fires on `/clear`
- ⬜ Verify `.cleared.json` files are created correctly

**Success Criteria**: After running `/clear`, a `.cleared.json` file exists with first message and files touched.

### Phase 2: Summarization Subagent
- ⬜ Create `session-summarizer.md` agent definition
- ⬜ Update hook to spawn agent in background
- ⬜ Test agent reads transcript and updates `.cleared.json`
- ⬜ Handle edge cases (empty sessions, very long sessions)

**Success Criteria**: `.cleared.json` files contain meaningful summaries generated by the agent.

### Phase 3: Browse Command
- ⬜ Create `/prior-sessions` slash command
- ⬜ Test browsing sessions in current project
- ⬜ Test searching/filtering
- ⬜ Test cross-project browsing

**Success Criteria**: Can easily find and reference cleared sessions by topic, date, or files.

### Phase 4: Polish & Documentation
- ⬜ Add error handling and logging
- ⬜ Write installation instructions
- ⬜ Add configuration options
- ⬜ Create examples and demos

## Open Questions

1. ✅ **Hook type**: Confirmed - use SessionEnd hook (not UserPromptSubmit)
2. ✅ **Agent invocation**: Use `claude --print --agent session-summarizer` from hook script
3. ✅ **Hook input schema**: SessionEnd provides: session_id, transcript_path, cwd, reason, permission_mode
4. ⬜ **Performance**: How fast is JSONL parsing for large sessions (1000+ messages)? May need optimization.
5. ⬜ **Agent timeout**: Should we add a timeout to the agent invocation to prevent hook hanging?
6. ⬜ **Error handling**: What happens if the agent fails? Should we write partial metadata anyway?

## Success Metrics

**Qualitative**:
- Can find a specific cleared session within 10 seconds
- Summaries are accurate and helpful
- No noticeable slowdown when running `/clear`

**Quantitative**:
- Hook execution time: < 100ms (for fast extraction)
- Agent summarization time: < 5 seconds (running in background)
- Storage overhead: < 10KB per cleared session

## Future Enhancements

- **Session threading**: Link related sessions (e.g., resumed from each other)
- **Export sessions**: Generate markdown reports from cleared sessions
- **Session tags**: Manual or auto-generated tags for organization
- **Search improvements**: Semantic search across summaries
- **Cleanup**: Auto-archive sessions older than N days
- **Statusline integration**: Show indicator when in a resumed session

---

## References

### Official Documentation
- **[SessionEnd Hook](https://code.claude.com/docs/en/hooks#sessionend)** - Hook that fires when sessions end
- **[Hooks Guide](https://code.claude.com/docs/en/hooks-guide)** - Complete guide to Claude Code hooks
- **[Sub-agents](https://code.claude.com/docs/en/sub-agents)** - How to define and use custom agents
- **[CLI Reference](https://code.claude.com/docs/en/cli-reference)** - Claude CLI flags and options
- **[Plugins](https://code.claude.com/docs/en/plugins)** - Plugin structure and distribution

### Related Research
- **[SESSION_TRACKER.md](SESSION_TRACKER.md)** - Original research and examples
- **Claude Code Session Transcripts** - Simon Willison's tools for transcript analysis

---

## Next Steps

1. ✅ Create this plan document
2. ✅ Research official hooks and agent documentation
3. ✅ Define SessionEnd hook + agent invocation architecture
4. ⬜ Create test hook inputs (mock SessionEnd JSON)
5. ⬜ Begin Phase 1 implementation (hook script + agent definition)
6. ⬜ Test with real `/clear` invocations
