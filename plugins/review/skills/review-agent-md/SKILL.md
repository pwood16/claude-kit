---
name: review-agent-md
description: Use when reviewing a CLAUDE.md, AGENTS.md, GEMINI.md, .cursorrules, or copilot-instructions file for bloat, unpaired don'ts, vague rules, or AGENTS.md best-practice adherence. Triggers: "review this CLAUDE.md", "lint my agent context", "what did I just add to CLAUDE.md", or /review-agent-md.
---

# review-agent-md

Score an agent-context markdown file against the AGENTS.md best practices distilled from [Augment Code's post](https://www.augmentcode.com/blog/how-to-write-good-agents-dot-md-files). Output is a terse PASS/WARN/FAIL scorecard with line-number citations — report-only, user fixes.

## When to use

| User says | Mode |
|-----------|------|
| `/review-agent-md <path>` or "review this CLAUDE.md" | Full-file rubric on the named file |
| `/review-agent-md` with no path | Discover & rubric all agent-context files in cwd |
| "what did I just add", "review the changes", "newly added parts" | Diff-only mode (working tree vs HEAD) |

Skip this skill for `.claude/skills/*/SKILL.md` — `superpowers:writing-skills` owns that rubric.

## Mode detection

Decide on the FIRST line of output, before scoring. Announce the mode you picked.

| Signal in user message | Mode |
|------------------------|------|
| Intent words: "added", "newly", "changed", "we just", "what we added", "new parts" | **Diff-only** |
| Otherwise (plain "review", "rubric", "lint", "is this clean") | **Full-file** |
| Ambiguous + file has uncommitted changes | Default diff-only; mention full-file is one ask away |

In diff-only mode:

1. `git diff HEAD -- <file>` to get working-tree changes.
2. If empty, `git diff HEAD~1 HEAD -- <file>` for the last commit's changes.
3. Extract added-line numbers (post-change line numbers in the current file).
4. Apply the rubric to the **whole** file for context, but only **flag** violations whose offending line is in the added set. Pre-existing problems are out of scope.

## Discovery (no-path invocation)

When invoked with no path, list candidates from these names — repo root + one subdir level:

- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`
- `.cursorrules`
- `.github/copilot-instructions.md`

Excluded by default (different rubric or different owner):

- `.claude/skills/*/SKILL.md` → use `superpowers:writing-skills`
- `.claude/commands/*.md` → different shape; user can pass explicitly

Show the discovered list, get a Y/n, then rubric each.

## The rubric

Apply each rule. Cite specific line numbers on every WARN/FAIL.

| # | Rule | WARN | FAIL | What "Do" looks like |
|---|------|------|------|----------------------|
| 1 | **Length** — sweet spot 100–150 lines | >200 lines | >400 lines | Push detail into reference files; link them |
| 2 | **Progressive disclosure** — references over inlining | length >150 AND zero outbound links to other .md/skills/paths | — | Add "See `<other.md>` for details" lines |
| 3 | **Procedural workflows numbered** | sequence words ("first/then/next/finally") in prose with no numbered list within 5 lines | — | Convert to `1./2./3.` numbered list |
| 4 | **Decision tables** — A-vs-B in prose | alternatives ("vs", "instead of", "or use", "either/or") with no markdown table within 10 lines | — | Add a table with one row per alternative |
| 5 | **Code examples** — short prod snippets | zero fenced code blocks AND file is technical (commands, language names, paths) | — | Add 1–3 snippets, 3–10 lines, from real prod code |
| 6 | **Rule specificity** — enforceable | — | vague verbs ("write clean code", "be careful", "follow conventions", "make sure", "do the right thing", "appropriate") | Replace with a concrete, enforceable rule (specific command, identifier, or check) |
| 7 | **Paired Don't/Do** | — | each unpaired "Don't / Never / Avoid / Do not" not within ~3 lines of a positive directive on the same subject | Append "Do <positive> instead" on the same bullet, or add a paired "Do" line |
| 8 | **Architecture bloat** — long "Why" sections | heading containing "Architecture / Overview / Why / Background / History" totals >30 lines of prose | — | Trim to "what" not "why"; move "why" to a separate doc |
| 9 | **Warning density** — Don't/Never/Avoid count | ≥10 negatives in file | ≥20 negatives | Cut to ≤5 most critical; pair each with a Do |

Rules 6 and 7 are FAILs because they cause the harms the Augment post documents (bloat from unpaired don'ts; rabbit-holes from vague rules). Everything else is WARN.

## Output format

```
## review-agent-md — <relative-path> (<n> lines)
Mode: full-file  |  diff-only (<n> lines added vs HEAD)

PASS   1. Length (<n>/150 line target)
PASS   2. Progressive disclosure (refs <n> other docs)
WARN   3. Procedural workflows — "first…then…finally" prose at L<x>; convert to numbered list
WARN   4. Decision tables — A-vs-B prose at L<x>-<y>; could be a 2-row table
WARN   5. Code examples — 0 fenced blocks in a technical file; add 1–3 short snippets
PASS   6. Rule specificity (all rules concrete)
FAIL   7. Paired Don't/Do — <k> unpaired negatives:
         L8:  "auto-generated, don't edit"          → pair with "Do regen via /<skill>"
         L16: "Never hand-edit"                     → pair with "Do rebuild via /brain"
         L36: "Never modify files in brain/raw/"    → pair with "Do edit the source repo"
PASS   8. Architecture bloat (no long Why sections)
PASS   9. Warning density (<n> negatives, under 10)

Verdict: 1 FAIL · 3 WARN · 5 PASS
Top fixes:
  1. Pair the 3 unpaired Don'ts at L8, L16, L36
  2. Add 1–3 short code snippets (commands you actually run)
  3. Convert the "first/then" prose at L<x> into a numbered list
```

Final line: "Report-only — paste a Don't line and I'll suggest a Do, but I won't auto-edit."

## Workflow

1. **Decide mode** from the user's wording (Mode detection table). Announce it on line 2 of output.
2. **Resolve target(s)**: path arg → that file. Glob → expand. No arg → run discovery, show list, confirm.
3. **Load context**: read the file fully. In diff-only mode, also run `git diff` to get the added-line set. Strip YAML frontmatter from line-count math but keep it visible to the rubric.
4. **Apply each rule** in order. Cite line numbers in every WARN/FAIL. Skip rules whose preconditions don't apply (e.g., rule 2 on a 55-line file → PASS by default).
5. **Compose the scorecard** in the exact shape above. One line per rule. Indent FAIL details.
6. **Verdict** line with counts + top 1–3 fixes ordered by severity (FAILs first; then WARNs ranked smallest-fix-biggest-impact).
7. **Report only.** If the user explicitly asks to fix afterward, that's a separate Edit operation, not part of this skill.

## Detection heuristics

**Negative directives (rule 7):** case-insensitive match on lines containing `\b(Don't|Never|Avoid|Do not)\b`. For each match, scan the next 3 lines for a positive directive `\b(Do|Use|Prefer|Always)\b` referring to the same subject. None found → unpaired → FAIL line item.

**Vague rules (rule 6):** case-insensitive match on phrases: "write clean code", "be careful", "follow conventions", "make sure", "do the right thing", "good code", "appropriate", "as needed", "best practices" (when used as a standalone instruction, not when pointing at a doc).

**Sequence indicators (rule 3):** "first", "then", "next", "finally", "before that", "after that", "step 1" in prose. If 3+ of these span consecutive bullets/sentences without `^\d+\.` numbered formatting nearby, flag.

**Decision-alternative indicators (rule 4):** "X vs Y", "X or Y", "either X or Y", "instead of X use Y", "X, while Y" — when describing technical choices. Skip if a markdown table (`|...|`) appears within 10 lines.

**Technical-file heuristic (rule 5):** file mentions any of `make `, `npm `, `pnpm `, `git `, `python`, `node`, `cargo`, `docker`, `psql`, file paths with `/` and an extension. Technical + zero fenced blocks → WARN.

**Architecture-section detection (rule 8):** heading line matching `Architecture|Overview|Why|Background|History` (case-insensitive). Count lines until next heading of same or higher level. >30 lines of prose (not list/table/code) → WARN.

## Common mistakes

- **Flagging every "Never" in headers or quotes.** Skip negatives that appear inside fenced code, blockquotes, or table cells used as data — they're not directives.
- **Counting frontmatter in line totals.** Strip YAML frontmatter before measuring length.
- **Over-pairing rule 7.** A general "Always cite source files" 20 lines away from "Never modify brain/raw/" isn't a pair — pairing requires the same subject and close proximity (~3 lines).
- **Treating PASSes as "nothing to mention".** Still print the PASS line — the user wants the full scorecard, not just failures.
- **Skipping diff context.** In diff-only mode, still read the whole file for context; only restrict *flagging* to added lines.
- **Auto-editing.** Do not. Report-only. A fix request after the report is a separate Edit operation.

## Red flags — stop and re-check

- About to suggest "add a section about X" → that's bloat; this rubric is subtractive hygiene more than additive.
- About to make a generic recommendation ("consider being more specific") → cite the exact line and propose a concrete replacement, or skip.
- About to auto-edit the file → don't. Report only.
- Scorecard exceeding ~30 lines → trim. Each rule = one line + indented FAIL details only.
