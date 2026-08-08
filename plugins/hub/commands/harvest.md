---
description: Close out a finished dispatch — record what shipped in its task file, then tear down the workspace, session and leftovers. The closing half of /dispatch.
argument-hint: "[optional: session name, slug, or task file path]"
---

Invoke the `harvest` skill (from the `hub` plugin) with arguments: `$ARGUMENTS`.

If `$ARGUMENTS` names a session, slug, or task file → harvest that dispatch.
If empty → list every `status: running` task file in `~/dev/hub/tasks/` alongside `tmux ls`, show which
have merged PRs, and ask which to harvest.

Follow the skill's workflow exactly. Two ordering rules carry the most weight:

- **Ask the session for its undispatched findings before killing it.** That answer is unrecoverable
  afterwards, and on a long-running session it is often the most valuable thing it holds.
- **Flip the task file's `status:` and `tmux kill-session` in the same step**, so the fleet is never
  recorded in a state it is not actually in.

Establish what shipped from the repo rather than from the session's own report; the two disagree more
often than expected.
