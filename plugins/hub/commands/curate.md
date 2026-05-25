---
description: Triage configured sources and ad-hoc URLs into brain/inbox.md; flag contradictions with active work as tasks/alert-*.md.
argument-hint: "[<url> | add <url> [tier] | remove <name-or-url>]"
---

Invoke the `curate` skill (from the `hub` plugin) with arguments: `$ARGUMENTS`.

Argument routing — apply precedence in this exact order:
1. Starts with `add` → registry add (use the skill's `add` semantics).
2. Starts with `remove` → registry remove (use the skill's `remove` semantics — everything after `remove` is the match string; preserve quoted multi-word names).
3. Matches `^https?://` → single-URL triage.
4. Empty `$ARGUMENTS` → full registry run.
5. Anything else → refuse and print the usage block from the skill.

See the skill's `Argument parsing notes` and `Required-token preconditions` sections for the exact handling of edge cases (missing URL after `add`, extra tokens, bad tier, etc.). Do not guess — refuse and print usage.

Follow the skill's workflow exactly. Load the three named memories the skill references (`feedback-source-typing-taxonomy`, `user-ai-discourse-posture`, `user-agent-reality-calibration`) before triaging any item — they encode Phil's calibration.
