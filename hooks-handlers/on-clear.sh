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

# Calculate timestamps (get first user message timestamp, not file-history-snapshot)
started_at=$(jq -s '[.[] | select(.type == "user") | select(.timestamp)][0].timestamp // ""' "$transcript_path")
cleared_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Extract files touched (Write and Edit tool uses)
files_touched=$(jq -s '[
  .[] |
  select(.type == "assistant") |
  .message.content[]? |
  select(.type == "tool_use") |
  select(.name == "Write" or .name == "Edit") |
  .input.file_path
] | unique' "$transcript_path")

# Phase 1: Write metadata immediately with empty title/summary
# This ensures we capture session data even if LLM call fails
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
    "started_at": $started_at
  },
  "content": {
    "first_message": $(printf '%s' "$first_message" | jq -Rs .),
    "files_touched": $files_touched,
    "title": "",
    "summary": ""
  }
}
EOF

# Phase 2: Background the slow LLM call to fill in title/summary
# This allows /clear to return immediately without blocking
# Use nohup and redirect all output to prevent blocking
nohup bash -c "
  transcript_content=\$(head -c 100000 \"$transcript_path\")

  agent_output=\$(echo \"\$transcript_content\" | claude --print \
    --agent session-summarizer \
    --output-format json \
    --json-schema '{\"type\":\"object\",\"properties\":{\"title\":{\"type\":\"string\"},\"summary\":{\"type\":\"string\"}},\"required\":[\"title\",\"summary\"]}' \
    'Summarize this Claude Code session transcript:' 2>/dev/null) || exit 0

  title=\$(echo \"\$agent_output\" | jq -r '.structured_output.title // \"\"')
  summary=\$(echo \"\$agent_output\" | jq -r '.structured_output.summary // \"\"')

  tmp=\$(mktemp)
  jq --arg t \"\$title\" --arg s \"\$summary\" \
    '.content.title = \$t | .content.summary = \$s' \
    \"$cleared_json_path\" > \"\$tmp\" && mv \"\$tmp\" \"$cleared_json_path\"
" </dev/null >/dev/null 2>&1 &

exit 0
