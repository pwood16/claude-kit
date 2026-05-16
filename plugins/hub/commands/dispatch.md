---
description: Hand off work to a background Claude in a tmux session, with a worktree workspace by default. Use after a thinking session when the next move is execution, not more discussion.
argument-hint: "[optional: workspace path or ticket id]"
---

Invoke the `dispatch` skill (from the `hub` plugin) with arguments: `$ARGUMENTS`.

If `$ARGUMENTS` is a path → infer workspace mode from the shape (worktree vs own-folder).
If `$ARGUMENTS` looks like a ticket id → use it as the session-name prefix.
If empty → resolve workspace, prompt, and naming interactively per the skill's workflow.

Follow the skill's workflow exactly — always run preflight and prompt validation before launch; never skip them. The main thread does the human-judgment steps; hand off the mechanical launch to a foreground `general-purpose` subagent per Step 7.
