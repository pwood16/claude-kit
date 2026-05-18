---
description: Rubric a CLAUDE.md / AGENTS.md / GEMINI.md / .cursorrules / copilot-instructions file against 12 best-practice rules (Anthropic-canonical + Augment-derived). Optional path argument; no path triggers discovery.
argument-hint: "[path-to-file] (optional)"
---

Invoke the `review-agent-md` skill (from the `review` plugin) with arguments: `$ARGUMENTS`.

If `$ARGUMENTS` is empty, run discovery in the current working directory. If a path is given, rubric that single file. Detect full-file vs diff-only mode per the skill's mode-detection table.

Report-only — do not edit the file under review.
