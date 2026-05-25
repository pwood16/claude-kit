---
name: review-agent-md
description: Use when reviewing a CLAUDE.md, AGENTS.md, GEMINI.md, .cursorrules, or copilot-instructions file for bloat, scope creep, excluded-content categories, unpaired don'ts, vague rules, staleness, or general best-practice adherence. Triggers: "review this CLAUDE.md", "lint my agent context", "what did I just add to CLAUDE.md", or /review-agent-md.
---

# review-agent-md

Score an agent-context markdown file against best-practice rules. Canonical source: Anthropic's [Write an effective CLAUDE.md](https://code.claude.com/docs/en/best-practices) section and the [large-codebases best-practices article](https://claude.com/blog/how-claude-code-works-in-large-codebases-best-practices-and-where-to-start). Practitioner-tier corroboration: [Augment Code's AGENTS.md post](https://www.augmentcode.com/blog/how-to-write-good-agents-dot-md-files). Output is a terse PASS/WARN/FAIL scorecard with line-number citations — report-only, user fixes.

## When to use

| User says | Mode |
|-----------|------|
| `/review-agent-md <path>` or "review this CLAUDE.md" | Full-file rubric on the named file |
| `/review-agent-md` with no path | Discover & rubric all agent-context files in cwd |
| "what did I just add", "review the changes", "newly added parts" | Diff-only mode (working tree vs HEAD) |

Skip this skill for any `**/skills/*/SKILL.md` — those have their own rubric (`audit-agent-skill` in this repo, or `superpowers:writing-skills`).

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
4. Apply the rubric to the **whole** file for context, but only **flag** violations whose offending line is in the added set. Pre-existing problems are out of scope. **Exception — file-level rules:** rule 1 (length), rule 11 (negative density), and rule 12 (temporal staleness) are whole-file properties without a single "added line". Skip them in diff-only mode rather than reporting against the pre-existing file.

## Discovery (no-path invocation)

When invoked with no path, list candidates from these names — repo root + one subdir level:

- `AGENTS.md`, `CLAUDE.md`, `CLAUDE.local.md`, `GEMINI.md`
- `.cursorrules`
- `.github/copilot-instructions.md`

Excluded by default (different rubric or different owner):

- `**/skills/*/SKILL.md` → use `audit-agent-skill` (or `superpowers:writing-skills`)
- `.claude/commands/*.md` → different shape; user can pass explicitly

Show the discovered list, get a Y/n, then rubric each.

## The rubric

Apply each rule. Cite specific line numbers on every WARN/FAIL.

| # | Rule | WARN | FAIL | What "Do" looks like |
|---|------|------|------|----------------------|
| 1 | **Length** — sweet spot 100–150 lines (effective, including `@imports`) | effective >200 | effective >400 | Push detail into reference files; link them |
| 2 | **Progressive disclosure** — references over inlining | effective length >150 AND zero outbound links/imports (auto-PASS if shell <60 lines + ≥2 `@imports`); also WARN if any `@import` target is missing | — | Add "See `<other.md>`" or `@path/to/import` lines; fix broken imports |
| 3 | **Scope-broadness** — only include things that apply broadly | section >15 lines that's domain-specific (one feature, module, or workflow) | — | Convert to a skill — Anthropic: for domain knowledge or workflows that are only relevant sometimes, use skills instead |
| 4 | **Excluded-content categories** — match Anthropic's ❌ list | file-by-file lists (≥3 bullets each naming a single file), inline API docs, frequent-change info (versions/dates/counts), long prose tutorials | — | Trim, link to external docs, or convert to a skill |
| 5 | **Procedural workflows numbered** | sequence words ("first/then/next/finally") in prose with no numbered list within 5 lines | — | Convert to `1./2./3.` numbered list |
| 6 | **Decision tables** — A-vs-B in prose | alternatives ("vs", "instead of", "or use", "either/or") with no markdown table within 10 lines | — | Add a table with one row per alternative |
| 7 | **Code examples** — short prod snippets | zero fenced code blocks AND file is technical (commands, language names, paths) | — | Add 1–3 snippets, 3–10 lines, from real prod code |
| 8 | **Rule specificity** — enforceable | — | vague verbs ("write clean code", "be careful", "follow conventions", "make sure", "do the right thing", "appropriate") | Replace with a concrete, enforceable rule (specific command, identifier, or check) |
| 9 | **Paired Don't/Do** | — | each unpaired "Don't / Never / Avoid / Do not" not within ~3 lines of a positive directive on the same subject | Append "Do <positive> instead" on the same bullet, or add a paired "Do" line |
| 10 | **Architecture bloat** — long "Why" sections | heading containing "Architecture / Overview / Why / Background / History" totals >30 lines of prose | — | Trim to "what" not "why"; move "why" to a separate doc |
| 11 | **Negative density** — Don't/Never/Avoid count (NOT IMPORTANT/YOU MUST) | ≥10 negatives in file | ≥20 negatives | Cut to ≤5 most critical; pair each with a Do |
| 12 | **Temporal staleness** — last meaningful edit age | last commit touching the file >180 days ago | — | Audit content against current model behavior; Anthropic recommends a 3–6 month cadence |

Rules 1, 8, 9, and 11 escalate to FAIL above their hard thresholds — those are the cases Anthropic + Augment document as causing real adherence loss ("Bloated CLAUDE.md files cause Claude to ignore your actual instructions"). Self-evident generic advice ("write clean code", "DRY", "use meaningful names") is owned by rule 8's vague-rule FAIL, not rule 4 — rule 4 covers the *other* exclusion categories (file-by-file lists, inline API docs, frequent-change info, long tutorials).

## Output format

```
## review-agent-md — <relative-path> (<n> lines · effective <m> w/ @imports)
Mode: full-file  |  diff-only (<n> lines added vs HEAD)
Last meaningful commit: <YYYY-MM-DD> (<k> days ago)

PASS   1. Length (<m>/150 effective)
PASS   2. Progressive disclosure (refs <n> docs, <i> @imports)
WARN   3. Scope-broadness — "X feature" section L<x>-<y> is domain-specific; convert to a skill
WARN   4. Excluded content — file-by-file list at L<x>-<y>; trim or link
WARN   5. Procedural workflows — "first…then" prose at L<x>; convert to numbered list
WARN   6. Decision tables — A-vs-B prose at L<x>-<y>; could be a 2-row table
PASS   7. Code examples (<n> fenced blocks)
FAIL   8. Rule specificity — <k> vague rules:
         L<x>: "write clean code"          → replace with a concrete check
FAIL   9. Paired Don't/Do — <k> unpaired negatives:
         L<x>: "Never hand-edit"           → pair with "Do regen via /<skill>"
PASS  10. Architecture bloat
PASS  11. Negative density (<n> negatives, under 10)
WARN  12. Temporal staleness — last edit <YYYY-MM-DD> (<k> months); audit for current model

Verdict: 2 FAIL · 5 WARN · 5 PASS
Top fixes:
  1. Replace vague "write clean code" at L<x> with a concrete enforceable rule
  2. Pair the unpaired "Never hand-edit" at L<x>
  3. Trim the domain-specific "X feature" section or move it to a skill
```

Final line: "Report-only — paste a Don't line and I'll suggest a Do, but I won't auto-edit."

## Workflow

1. **Decide mode** from the user's wording (Mode detection table). Announce it on line 2 of output.
2. **Resolve target(s)**: path arg → that file. Glob → expand. No arg → run discovery, show list, confirm. **Early stop:** if the resolved path matches `**/skills/*/SKILL.md`, emit a one-liner ("This is a SKILL.md — use `audit-agent-skill` for that rubric") and stop. The CLAUDE.md rubric mis-fires wholesale on SKILL.md content (rules 1, 3, 4, 10 will all complain about content that's correct for a skill).
3. **Load context**: read the file fully. Strip YAML frontmatter from line-count math but keep it visible to the rubric. Resolve `@path` imports (one level deep) and sum their non-frontmatter line counts into the effective length. In diff-only mode, also run `git diff` to get the added-line set.
4. **Capture age** (full-file only): `git log -1 --format=%ct -- <file>` → unix timestamp. Age in days = `(now - timestamp) / 86400`. If the file isn't tracked or git isn't available, skip rule 12.
5. **Apply each rule** in order. Cite line numbers in every WARN/FAIL. Skip rules whose preconditions don't apply (e.g., rule 2 on a 55-line file → PASS by default).
6. **Compose the scorecard** in the exact shape above. One line per rule. Indent FAIL details.
7. **Verdict** line with counts + top 1–3 fixes ordered by severity (FAILs first; then WARNs ranked smallest-fix-biggest-impact).
8. **Report only.** If the user explicitly asks to fix afterward, that's a separate Edit operation, not part of this skill.

## Detection heuristics

**`@import` resolution (rules 1 & 2):** Scan the file for `@`-prefixed paths matching `(^|\s)@(~/)?[A-Za-z0-9._/-]+\.(md|txt)\b` (also valid inline mid-sentence). Require a whitespace or line-start before `@` so emails (`user@example.com`) and word-internal `@`s don't match. **Skip matches inside fenced code blocks (` ``` `) and inline code (`` ` ``)** — a bash example like `` `cat @file.txt` `` is not a CLAUDE.md import directive.

For each remaining match, resolve:

- `@~/...` → expand from `$HOME`
- otherwise → relative to the directory of the file under review

If the target exists, count its lines (strip frontmatter). Sum into `effective_length` alongside the shell file's line count. **If the target is missing, WARN under rule 2** with the line citation — broken imports are a high-signal staleness indicator. Don't recurse — one level only. Use `effective_length` for rule 1 thresholds. For rule 2, if the file's *shell* length is under 60 lines but it has ≥2 resolvable `@imports` or ≥3 outbound link references (`[text](url)`, bare URLs, or backtick-quoted paths like `` `docs/foo.md` ``), it's already practicing progressive disclosure → **PASS** (don't WARN on a thin import-heavy shell).

**Scope-broadness (rule 3):** Look for sections that talk about a specific feature, subsystem, file, or workflow only relevant when working on that area. Indicators:

- Headings or bullets naming a single subsystem/feature (e.g., "## Auth flow", "## Billing module", "When working on X")
- Long file lists (≥3 consecutive bullets each describing one file)
- Workflow steps tied to one feature ("To add a new endpoint to the X API, do…")
- Phrases: "when working on", "when you're touching", "for the X module", "in the X subsystem"

Skip the rule if the file is short (<50 effective lines) — small files don't bloat enough to justify a skill split.

**Excluded-content categories (rule 4):** Match against Anthropic's ❌ list. Distinct sub-checks (cite the most-specific one that fires):

- **File-by-file descriptions** — 3+ consecutive bullets shaped like `` `<path>` — <one-liner> `` where each path names a single file (extension or no trailing `/`). **Directory-layout lists** (paths ending in `/`, e.g., `` `brain/` — AI-maintained wiki ``) are legitimate workspace orientation, not "file-by-file" bloat — don't flag.
- **Inline API docs** — function signatures with parameter/return docstrings, or HTTP method + path + params blocks; should be a link
- **Frequent-change info** — specific dates ("as of 2025-09-12", "last updated"), version numbers in main body (`v1.2.3`, "running 2.4.x"), counts of teams/services/people that drift
- **Long tutorials/explanations** — contiguous prose block >25 lines with no list/table/code interruption

Self-evident generic advice ("write clean code", "DRY", "use meaningful names") is owned by rule 8's vague-verb FAIL, not rule 4 — don't double-cite. Rule 4 fires only on the four content categories above.

**Negative directives (rule 9):** case-insensitive match on lines containing `\b(Don't|Never|Avoid|Do not)\b`. For each match, scan the next 3 lines for a positive directive `\b(Do|Use|Prefer|Always)\b` referring to the same subject. None found → unpaired → FAIL line item.

**Vague rules (rule 8):** case-insensitive match on phrases: "write clean code", "be careful", "follow conventions", "make sure", "do the right thing", "good code", "appropriate", "as needed", "best practices", "use meaningful names", "keep functions small", "test edge cases", "be consistent", "refactor as needed", "DRY" (when used as a standalone instruction, not when pointing at a doc).

**Sequence indicators (rule 5):** "first", "then", "next", "finally", "before that", "after that", "step 1" in prose. If 3+ of these span consecutive bullets/sentences without `^\d+\.` numbered formatting nearby, flag.

**Decision-alternative indicators (rule 6):** "X vs Y", "X or Y", "either X or Y", "instead of X use Y", "X, while Y" — when describing technical choices. Skip if a markdown table (`|...|`) appears within 10 lines.

**Technical-file heuristic (rule 7):** file mentions any of `make `, `npm `, `pnpm `, `git `, `python`, `node`, `cargo`, `docker`, `psql`, file paths with `/` and an extension. Technical + zero fenced blocks → WARN.

**Architecture-section detection (rule 10):** heading line matching `Architecture|Overview|Why|Background|History` (case-insensitive). Count lines until next heading of same or higher level. >30 lines of prose (not list/table/code) → WARN.

**Negative density (rule 11):** count lines containing `\b(Don't|Never|Avoid|Do not)\b`. **Do NOT count `IMPORTANT`, `YOU MUST`, `CRITICAL`, or other positive-emphasis markers** — Anthropic explicitly recommends these for tuning adherence (best-practices doc: "You can tune instructions by adding emphasis (e.g., 'IMPORTANT' or 'YOU MUST') to improve adherence"). Counting them as negatives would penalize an endorsed pattern.

**Temporal staleness (rule 12):**

```bash
last_ts=$(git log -1 --format=%ct -- "$file" 2>/dev/null)
if [ -z "$last_ts" ]; then
  echo "skip rule 12 — file not tracked in git"
else
  age_days=$(( ($(date +%s) - last_ts) / 86400 ))
fi
```

WARN if `age_days > 180`. Skip silently if the file isn't tracked or git isn't available. Don't FAIL — model evolution doesn't make every old file broken; it just makes audit overdue.

## Common mistakes

- **Flagging every "Never" in headers or quotes.** Skip negatives inside fenced code, blockquotes, or table cells used as data — they're not directives.
- **Counting frontmatter in line totals.** Strip YAML frontmatter before measuring length, both for the shell file and for `@import` targets.
- **Forgetting `@import` math.** A 50-line shell + 200 lines of imports is a 250-line CLAUDE.md in practice. Use the effective length for rule 1.
- **WARN-ing a thin import shell on rule 2.** A 40-line file with 3 `@imports` is doing progressive disclosure right; PASS rule 2.
- **Matching `@imports` inside code.** `` `cat @file.txt` `` in a bash example is not an import — skip code-fenced and inline-code regions.
- **Flagging directory-layout bullets as file-by-file (rule 4).** Paths ending in `/` are workspace orientation, not redundant per-file docs.
- **Counting IMPORTANT/YOU MUST as negatives** (rule 11) — Anthropic recommends them. Only Don't/Never/Avoid/Do not count.
- **Over-pairing rule 9.** A general "Always cite source files" 20 lines away from "Never modify brain/raw/" isn't a pair — pairing requires the same subject and close proximity (~3 lines).
- **Treating PASSes as "nothing to mention".** Still print the PASS line — the user wants the full scorecard, not just failures.
- **Verbose FAIL detail blocks.** Cap each FAIL's indented detail lines at 3; append "(+N more)" if there are extra hits — preserves the ~35-line scorecard ceiling.
- **Skipping diff context.** In diff-only mode, still read the whole file for context. Only restrict *flagging* to added lines, and skip rules 1, 11, and 12 entirely (whole-file properties).
- **Running this on a SKILL.md.** Stop and redirect to `audit-agent-skill` — the rubrics don't transfer.
- **Auto-editing.** Do not. Report-only. A fix request after the report is a separate Edit operation.

## Red flags — stop and re-check

- About to suggest "add a section about X" → that's bloat; this rubric is subtractive hygiene more than additive.
- About to make a generic recommendation ("consider being more specific") → cite the exact line and propose a concrete replacement, or skip.
- About to auto-edit the file → don't. Report only.
- Scorecard exceeding ~35 lines → trim. Each rule = one line + indented FAIL details only.
