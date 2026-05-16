---
description: Rubric one or more SKILL.md files against the 10-section agent-skill best-practices rubric (A–J). No path triggers discovery; a path argument scores that file (or all SKILL.md files under that dir).
argument-hint: "[path-to-SKILL.md-or-skills-dir] (optional)"
---

Invoke the `audit-agent-skill` skill (from the `review` plugin) with arguments: `$ARGUMENTS`.

If `$ARGUMENTS` is empty → discover every `SKILL.md` under `.claude/skills/`, `skills/`, and `plugins/*/skills/` in the current working directory; inventory them, confirm with the user, then rubric each.

If `$ARGUMENTS` is a path to a SKILL.md → rubric that single file.
If `$ARGUMENTS` is a directory → rubric every SKILL.md it contains.

Always run the inventory step first and surface the list before scoring. Report-only — do not edit any SKILL.md.
