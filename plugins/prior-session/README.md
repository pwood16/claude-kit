# Prior Sessions

Automatically capture and browse summaries of your cleared Claude Code sessions.

## What It Does

When you run `/clear` in Claude Code, this plugin:

1. **Captures session metadata** - session ID, timestamps, git branch, files touched
2. **Generates a summary** - uses an LLM to create a title and summary of what you accomplished
3. **Saves it for later** - stores a `.cleared.json` file alongside your transcript

Later, use the `/prior-session:browse` command to browse and search your cleared sessions.

## Usage

### Automatic Session Capture

Just use `/clear` as normal. The plugin automatically:
- Captures session metadata immediately (non-blocking)
- Generates title and summary in the background
- Saves everything to `~/.claude/projects/<project>/<session-id>.cleared.json`

### Browse Prior Sessions

```
/prior-session:browse
```

This displays your cleared sessions with:
- Date and time (oldest first, newest last)
- Title (5-8 words)
- Summary (2-3 sentences)
- Files touched

You can also search:
```
/prior-session:browse authentication bug
```

**Note**: You must be in the project directory to see sessions for that project. The command shows sessions from the current project by default.

## Components

### Hook: `hooks-handlers/on-clear.sh`

Triggered on SessionEnd when `/clear` is called. Extracts metadata and spawns the summarizer agent in the background.

### Agent: `agents/session-summarizer.md`

A Haiku-based agent that reads session transcripts and generates concise summaries.

### Command: `commands/browse.md`

Slash command to browse and search cleared sessions.

## Data Format

Session metadata is stored in `.cleared.json` files:

```json
{
  "version": "1.0",
  "session_id": "636bbf12-b19c-4cce-ae7c-d75133c7bfee",
  "cleared_at": "2026-01-03T03:58:39Z",
  "project": {
    "name": "my-project",
    "path": "/path/to/my-project",
    "git_branch": "main"
  },
  "transcript": {
    "path": "/path/to/transcript.jsonl",
    "message_count": 42,
    "started_at": "2026-01-03T02:00:00Z"
  },
  "content": {
    "first_message": "Help me implement...",
    "files_touched": ["src/auth.ts", "src/auth.test.ts"],
    "title": "Fixed OAuth token refresh bug",
    "summary": "Debugged and fixed OAuth token refresh..."
  }
}
```

## Requirements

- `jq` - for JSON parsing in the hook script
- `claude` CLI - for invoking the summarizer agent
