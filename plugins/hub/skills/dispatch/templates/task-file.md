---
type: spawn-agent
session: {{session}}
ticket: {{ticket}}
pr: {{pr}}
workspace: {{workspace}}
branch: {{branch}}
claude_project_dir: {{claude_project_dir}}
claude_name: {{session}}
claude_session_id: pending
launched_at: {{launched_at}}
status: running
---

## Prompt

{{prompt_body}}

## Harvest

<!-- Filled in by /harvest when this dispatch is closed out. Keep every heading; write "none" rather
     than deleting one, so a missing answer is visible instead of silent. -->

**Outcome** — PR, merge commit, diff size, whether it deployed:

**Scope delta** — what shipped that the brief did not ask for, or asked for and did not get:

**Verification** — what was actually run, and what was skipped:

**Residuals** — accepted gaps, in the session's own words:

**Loose ends** — databases, fixtures, remote branches, processes left behind:

**Findings nobody picked up** — what this session noticed that became nobody's work:

**Successor** — the spawn file or memo this hands off to, if any:
