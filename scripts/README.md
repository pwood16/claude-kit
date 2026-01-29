# Statusline Script

Enhanced statusline for Claude Code with comprehensive git status indicators.

## Features

- **Model & context**: Current Claude model and context window size
- **Git repository**: Repository name and current branch
- **File changes**:
  - `+N` staged files ready to commit
  - `!N` modified files (tracked but unstaged)
  - `?N` untracked files
  - `↑N` commits ready to push
  - `⚠` no upstream tracking branch
- **Token usage**: Running session token count
- **Color coding**:
  - 🔴 Red: Unstaged changes present
  - 🟡 Yellow: Staged/untracked/unpushed changes or missing upstream
  - 🟢 Green: Clean working tree

Example output:
```
[Sonnet 4.5 (1M context)] claude-kit:main [!1 ⚠] | 49,221 session tokens
```

## Installation

**Prerequisites**: `jq` for JSON parsing
```bash
brew install jq  # macOS
# or
apt-get install jq  # Linux
```

**Install**:
1. Copy the script to your Claude config directory:
   ```bash
   cp statusline.sh ~/.claude/statusline.sh
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

## Staying Up to Date

To automatically get updates when you pull this repo, use a symlink instead of copying:

```bash
ln -s /path/to/claude-kit/scripts/statusline.sh ~/.claude/statusline.sh
```

Then whenever you `git pull` the repo, the latest script is immediately available.

## Configuration

### Cache Duration
The script uses a 3-second cache to avoid expensive git operations on every render. Adjust the `CACHE_DURATION` variable in the script if needed.

### Customization
The script is designed to be easily customizable. Edit the script to:
- Modify colors (ANSI color codes at the top)
- Change status indicators
- Add or remove information fields
- Adjust formatting

## Resources

- [Official Claude Code Statusline Documentation](https://code.claude.com/docs/en/statusline)
