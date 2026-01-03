# Cleared Sessions - Implementation Plan

**For**: Coding agent to implement the cleared sessions feature
**Reference**: See [CLEARED_SESSIONS_PLAN.md](CLEARED_SESSIONS_PLAN.md) for architecture details
**Test Data**: `test/fixtures/sessionend-clear-normal.json`

---

## Prerequisites

**Required tools:**
- `jq` - JSON parsing (verify: `which jq`)
- `git` - Version control info
- `claude` CLI - Agent invocation

**Test fixture available:**
- `test/fixtures/sessionend-clear-normal.json` - Real SessionEnd hook data

**Repository structure:**
```
claude-kit/
├── .claude-plugin/plugin.json
├── hooks/hooks.json
├── hooks-handlers/on-clear.sh       ← CREATE THIS
├── agents/session-summarizer.md     ← CREATE THIS
├── commands/prior-sessions.md       ← CREATE THIS
└── test/fixtures/...
```

---

## Implementation Steps

### Phase 1: Create Agent Definition

**File**: `agents/session-summarizer.md`

**Requirements:**
1. Agent uses **haiku** model (fast and cheap)
2. No tools required (receives transcript content via stdin from hook script)
3. Generates structured JSON with `title` and `summary` fields
4. Title: 5-8 words
5. Summary: 2-3 sentences

**Implementation:**

```markdown
---
name: session-summarizer
description: Generates title and summary for cleared Claude Code sessions
model: haiku
---

You are a session summarizer for Claude Code. Your task is to analyze conversation transcripts and generate concise summaries.

## Your Task

You will receive a JSONL transcript (one JSON object per line). Analyze the conversation and generate:

1. **title** (5-8 words): A scannable label for quick identification
2. **summary** (2-3 sentences): Key accomplishments and outcomes

## Analysis Focus

- What was the user trying to accomplish?
- What was built, fixed, or explained?
- What files were modified?
- What was the final state when the session was cleared?

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

## Example Output

```json
{
  "title": "Fixed OAuth token refresh bug",
  "summary": "Debugged and fixed OAuth token refresh bug in auth.ts. Added error handling for expired tokens and edge case testing. Updated type definitions to support new error states."
}
```
```

**Validation:**
- File exists at `agents/session-summarizer.md`
- Contains YAML frontmatter with `name`, `description`, `model`
- Specifies `model: haiku`
- No tools specified (agent receives transcript via stdin, doesn't need file access)
- Instructions are clear and example-driven

---

### Phase 2: Create Hook Script

**File**: `hooks-handlers/on-clear.sh`

**Requirements:**
1. Read SessionEnd JSON from stdin
2. Only process if `reason == "clear"` (skip normal exits)
3. Exit gracefully if transcript doesn't exist
4. Extract basic metadata from JSONL (first message, file count, etc.)
5. Get git info from `cwd`
6. Invoke `session-summarizer` agent via `claude --print`
7. Write complete `.cleared.json` file next to transcript
8. Handle errors gracefully (empty summary if agent fails)

**Implementation:**

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
[ ! -f "$transcript_path" ] && exit 0

# Change to working directory for git commands
cd "$cwd" 2>/dev/null || cd ~

# Extract basic metadata from JSONL (fast operations)
first_message=$(jq -s '[.[] | select(.type == "user")][0].message.content // ""' "$transcript_path")
message_count=$(jq -s '[.[] | select(.type == "user")] | length' "$transcript_path")

# Get git info
git_branch=$(git branch --show-current 2>/dev/null || echo "")
git_repo=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" || basename "$cwd")

# Calculate timestamps
started_at=$(jq -s '.[0].timestamp // ""' "$transcript_path")
cleared_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Read transcript content (limit to reasonable size for agent context)
transcript_content=$(cat "$transcript_path")

# Invoke session-summarizer agent to get title + summary
# Pipe transcript content to agent via stdin
summary_json=$(echo "$transcript_content" | claude --print \
  --agent session-summarizer \
  --output-format json \
  --json-schema '{"type":"object","properties":{"title":{"type":"string"},"summary":{"type":"string"}},"required":["title","summary"]}' \
  "Summarize this Claude Code session transcript:" 2>/dev/null || echo '{"title":"","summary":""}')

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
    "first_message": $(echo "$first_message" | jq -Rs .),
    "files_touched": $files_touched,
    "title": $(echo "$title" | jq -Rs .),
    "summary": $(echo "$summary" | jq -Rs .)
  }
}
EOF

exit 0
```

**Testing the script:**

```bash
# Test with fixture (without actually calling agent)
cat test/fixtures/sessionend-clear-normal.json | bash hooks-handlers/on-clear.sh

# Check if .cleared.json was created
ls -la /Users/phil/.claude/projects/-Users-phil-Dev-repos-claude-kit/*.cleared.json

# View the output
cat /Users/phil/.claude/projects/-Users-phil-Dev-repos-claude-kit/*.cleared.json | jq .
```

**Validation:**
- Script exists at `hooks-handlers/on-clear.sh`
- Is executable (`chmod +x`)
- Reads JSON from stdin
- Only processes `reason: "clear"`
- Creates `.cleared.json` file with correct structure
- Handles missing transcript gracefully
- Escapes JSON strings properly with `jq -Rs`

---

### Phase 3: Create Hooks Configuration

**File**: `hooks/hooks.json`

**Requirements:**
1. Register SessionEnd hook
2. Point to hook script using relative path

**Implementation:**

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

**Note**: The `${CLAUDE_PLUGIN_ROOT}` variable is confirmed in the [Hooks Reference](https://code.claude.com/docs/en/hooks) documentation as an available environment variable for plugin hooks.

**Validation:**
- File exists at `hooks/hooks.json`
- Valid JSON syntax
- References hook script correctly

---

### Phase 4: Create /prior-sessions Command

**File**: `commands/prior-sessions.md`

**Requirements:**
1. Search for `*.cleared.json` files across projects
2. Display formatted list with title, summary, date, files
3. Support search/filtering
4. Show most recent sessions first

**Implementation:**

```markdown
---
description: Browse and search cleared Claude Code sessions
---

# Prior Sessions Command

Show my prior cleared sessions from this project (or all projects if I ask).

## Your Task

1. **Find cleared session files**:
   - Search for `*.cleared.json` files in `~/.claude/projects/`
   - Default: current project only (check if current directory matches any project path)
   - If I ask for "all projects", search all subdirectories

2. **Read and parse session metadata**:
   - Extract: title, summary, cleared_at, files_touched, project info
   - Sort by `cleared_at` descending (most recent first)
   - Default limit: 10 sessions

3. **Display formatted list**:

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

4. **Support interactions**:
   - If I provide a search term, filter by title/summary/files
   - If I ask "show more", display next batch
   - If I ask for a specific session ID, show full details

5. **Handle edge cases**:
   - No cleared sessions found → helpful message
   - Empty summaries → show first message instead
   - Missing files → show "No files recorded"
```

**Validation:**
- File exists at `commands/prior-sessions.md`
- Contains description in frontmatter
- Clear instructions for Claude
- Example output format provided

---

### Phase 5: Testing Strategy

**Test 1: Hook Script with Fixture (Offline)**

```bash
# Test hook processes fixture correctly
cat test/fixtures/sessionend-clear-normal.json | \
  bash hooks-handlers/on-clear.sh

# Verify output file created
test -f /Users/phil/.claude/projects/-Users-phil-Dev-repos-claude-kit/636bbf12-b19c-4cce-ae7c-d75133c7bfee.cleared.json && \
  echo "✅ Hook created .cleared.json" || \
  echo "❌ Hook failed to create .cleared.json"

# Check JSON structure
cat /Users/phil/.claude/projects/-Users-phil-Dev-repos-claude-kit/636bbf12-b19c-4cce-ae7c-d75133c7bfee.cleared.json | \
  jq -e '.version and .session_id and .content.title and .content.summary' && \
  echo "✅ JSON structure correct" || \
  echo "❌ JSON structure invalid"
```

**Test 2: Agent Invocation (Manual)**

```bash
# Test agent can be invoked and returns JSON
# Pipe transcript content directly to agent
cat /Users/phil/.claude/projects/-Users-phil-Dev-repos-claude-kit/636bbf12-b19c-4cce-ae7c-d75133c7bfee.jsonl | \
  claude --print \
  --agent session-summarizer \
  --output-format json \
  --json-schema '{"type":"object","properties":{"title":{"type":"string"},"summary":{"type":"string"}}}' \
  "Summarize this Claude Code session transcript:"

# Should output something like:
# {
#   "title": "Session tracker planning and testing",
#   "summary": "Created comprehensive plan for cleared sessions tracking..."
# }
```

**Test 3: End-to-End with Real /clear**

1. Install plugin hooks (if not already in settings.json)
2. Do some work in a session
3. Run `/clear`
4. Verify `.cleared.json` was created
5. Check summary quality

**Test 4: /prior-sessions Command**

```bash
# In Claude session
/prior-sessions

# Should display list of cleared sessions
# Verify formatting, titles, summaries are shown correctly
```

---

## Validation Checklist

**File Structure:**
- [ ] `agents/session-summarizer.md` exists
- [ ] `hooks-handlers/on-clear.sh` exists and is executable
- [ ] `hooks/hooks.json` exists
- [ ] `commands/prior-sessions.md` exists

**Agent Functionality:**
- [ ] Agent can be invoked with `claude --print --agent session-summarizer`
- [ ] Agent receives transcript content via stdin (piped from hook script)
- [ ] Agent returns valid JSON with `title` and `summary` fields
- [ ] Agent uses haiku model (fast/cheap)

**Hook Functionality:**
- [ ] Hook processes SessionEnd JSON correctly
- [ ] Hook only runs when `reason == "clear"`
- [ ] Hook extracts first message, files touched, message count
- [ ] Hook gets git info (branch, repo name)
- [ ] Hook invokes agent successfully
- [ ] Hook creates `.cleared.json` with correct structure
- [ ] Hook handles errors gracefully (missing transcript, failed agent)

**Command Functionality:**
- [ ] `/prior-sessions` finds `.cleared.json` files
- [ ] Command displays formatted list
- [ ] Titles and summaries are shown
- [ ] Files touched are listed
- [ ] Dates are formatted nicely
- [ ] Can search/filter sessions

**Integration:**
- [ ] Hook fires on `/clear` (test with real session)
- [ ] `.cleared.json` files are created in correct location
- [ ] Summaries are accurate and helpful
- [ ] `/prior-sessions` shows cleared sessions

---

## Known Issues / Edge Cases to Handle

1. **Transcript file might not exist** when hook fires
   - Solution: Check file exists before processing

2. **Agent invocation might fail** (API error, timeout)
   - Solution: Fallback to empty title/summary with `|| echo '{...}'`

3. **JSON escaping** in shell heredoc
   - Solution: Use `jq -Rs` to safely encode strings

4. **Large transcripts** might be slow to parse
   - Solution: Use `jq -s` for efficient JSONL processing
   - Agent only needs to read, not parse entire file

5. **Git repo might not exist** in `cwd`
   - Solution: Fallback to directory basename if git commands fail

6. **Multiple cleared sessions** in one project
   - Solution: Each gets own `.cleared.json` file (one per session_id)

---

## Success Criteria

**The implementation is complete when:**

1. ✅ Running `/clear` creates a `.cleared.json` file with title and summary
2. ✅ Running `/prior-sessions` shows a formatted list of cleared sessions
3. ✅ Titles are concise and descriptive (5-8 words)
4. ✅ Summaries are accurate and helpful (2-3 sentences)
5. ✅ Files touched are captured correctly
6. ✅ No errors or crashes during normal operation
7. ✅ Works in different projects/git repos
8. ✅ Handles edge cases gracefully (no git, empty sessions, etc.)

---

## Future Enhancements (Not in Scope)

- Auto-cleanup of old sessions (retention policy)
- Session tagging/categorization
- Semantic search across summaries
- Export sessions to markdown
- Statusline integration (show when in resumed session)

---

## References

- **Plan**: [CLEARED_SESSIONS_PLAN.md](CLEARED_SESSIONS_PLAN.md)
- **Test Fixture**: `test/fixtures/sessionend-clear-normal.json`
- **SessionEnd Hook Docs**: https://code.claude.com/docs/en/hooks#sessionend
- **CLI Reference**: https://code.claude.com/docs/en/cli-reference
- **Sub-agents Docs**: https://code.claude.com/docs/en/sub-agents
