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
