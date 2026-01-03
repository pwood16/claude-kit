# Claude Kit

Enhanced statusline for Claude Code with git status indicators.

## Features

- **Model & context**: Current Claude model and context window
- **Git status**: Repository, branch, and changes
  - `+N` staged files
  - `!N` modified files
  - `?N` untracked files
  - `↑N` unpushed commits
- **Token usage**: Session token count
- **Color-coded**: Red (unstaged changes), Yellow (staged/untracked/unpushed), Green (clean)

Example: `[Sonnet 4.5 (1M context)] claude-kit:main [?2] | 16,145 session tokens`

## Installation

**Prerequisites**: `jq` (`brew install jq`)

1. Copy the statusline script:
   ```bash
   cp scripts/statusline.sh ~/.claude/statusline.sh
   chmod +x ~/.claude/statusline.sh
   ```

2. Update `~/.claude/settings.json`:
   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "~/.claude/statusline.sh"
     }
   }
   ```

3. Restart Claude Code

## Configuration

Edit the `CACHE_DURATION` variable in the script to adjust cache timing (default: 3 seconds).
