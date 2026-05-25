---
name: audit-agent-skill
description: Use when auditing one or more SKILL.md files for adherence to best practices — description quality, progressive disclosure, paired Don't/Do, portability, delegation antipattern, evals. Triggers "audit this skill", "review my SKILL.md", "rubric the skills in this repo", "are these skills shippable", or /audit-agent-skill.
---

# audit-agent-skill

Score one or more `SKILL.md` files against the agent-skill best-practices rubric (10 sections, A–J). Canonical sources: Anthropic's [skills spec](https://code.claude.com/docs/en/skills) (progressive disclosure, loader tiers) and [agentskills.io best-practices](https://agentskills.io/skill-creation/best-practices) (calibration, defaults over menus, real-expertise grounding). Output is a per-skill verdict (ship-quality / needs work / rewrite) with quoted offending lines and concrete next edits. Report-only — no auto-edits.

## When to use

| User says | Mode |
|-----------|------|
| `/audit-agent-skill <path>` or "audit this skill" | Full rubric on the named SKILL.md (or every SKILL.md under the named directory) |
| `/audit-agent-skill` with no path | Discover every `SKILL.md` under `.claude/skills/`, `skills/`, and `plugins/*/skills/` in cwd, then rubric each |
| "what did I just add to this skill", "audit the changes" | Diff-only mode (working tree vs HEAD on the SKILL.md only) |

## When NOT to use

| Don't | Do instead |
|---|---|
| Audit a `CLAUDE.md` / `AGENTS.md` / `.cursorrules` file | Use `review-agent-md` — different rubric for agent-context files |
| Audit a reference file under `references/` | Skip — references inherit the skill's scope and don't have frontmatter |
| Auto-fix what the audit flags | Report only. Edits are a separate, explicit request after the user reads the verdict |
| Pad a thin scorecard with platitudes | Apply the tax test (section J) — if a rule passes trivially, mark PASS and move on |

## Workflow

### Step 1 — Inventory

For each SKILL.md found, capture: relative path, `name:`, `description:`, body length in lines (excluding frontmatter), and whether `references/`, `scripts/`, or `assets/` subdirs exist alongside.

Show the inventory before scoring so the user can opt out of any items.

### Step 2 — Apply the rubric

Score each skill against all 10 sections below. **Quote the offending line on every flagged issue** — paraphrasing is the most common failure mode.

#### A. Description (the most expensive line)

The description is loaded into context every session and routes which skill fires. It is not internal documentation.

- [ ] Starts with "Use when…" or "Load when…" (user-intent framing, not capability summary)
- [ ] ≤ 50 words
- [ ] Uses language a real engineer would use to describe the symptom or task (e.g. "babysit CI", "redirect loop"), not marketing-style capability prose
- [ ] Specific enough to NOT over-trigger on adjacent work
- [ ] Specific enough to actually fire when the situation matches

#### B. Progressive disclosure (loader architecture)

Skills load in three tiers: metadata (always), body (on trigger), references/scripts (on demand). Monolithic SKILL.md files waste context.

- [ ] SKILL.md body ≤ ~500 lines AND ≤ ~5,000 tokens (Anthropic spec / agentskills.io); ideally 100–150 lines
- [ ] Heavy or conditional content lives in `references/*.md`, loaded only when needed
- [ ] Each reference is loaded *conditionally* — the body says *when* to load it (e.g., "Read `references/api-errors.md` if the API returns non-200"), not a generic "see references/ for details"
- [ ] Deterministic logic the model would otherwise reconstruct lives in `scripts/`
- [ ] Reference files do NOT have YAML frontmatter (frontmatter promotes them to skill-level visibility; the agent may invoke them out of context)

#### C. Gotchas (the actual content)

The model already knows the obvious. The skill's job is to encode what the model would get wrong. If everything in the body is "easy to explain," the skill is mostly tax.

- [ ] Has an explicit gotchas / pitfalls / anti-pattern section
- [ ] Each gotcha names a specific failure mode the model would hit
- [ ] Every "Don't" is paired with a concrete "Do" (warnings alone underperform)
- [ ] Encodes environment- or domain-specific knowledge (build tools, conventions, monorepo layout) that isn't derivable from training data

#### D. Workflow vs prose

Skills are workflows with exit criteria, not essays.

- [ ] Steps are numbered, actionable, and checkable
- [ ] Each step has clear exit criteria (what "done" looks like)
- [ ] No long architectural overviews or rationale dumps in the body — those cause "context rot" by inviting the model to explore unrelated docs
- [ ] Has a sample output / report template if the skill produces structured output
- [ ] **Defaults over menus** (agentskills.io) — when multiple tools/approaches could work, the skill picks one default and mentions alternatives briefly. Long "you can use X or Y or Z" lists without a recommendation are a flag.
- [ ] **No explanations of well-known concepts** (agentskills.io) — the body doesn't define what a PDF/HTTP/database/etc. is. Skill content focuses on what the model *wouldn't* know without it.

#### E. Anti-rationalization

LLMs invent plausible reasons to skip steps under time pressure. Strong skills preempt this.

- [ ] Body addresses common excuses the model might generate (e.g. "I'll just check the code instead", "this seems simple enough")
- [ ] Verification or evidence is required before claiming completion (passing tests, screenshot, runtime trace, etc.)

#### F. Portability

Skills must work in environments other than the one they were authored in.

- [ ] No hardcoded paths assuming a specific repo layout
- [ ] No assumed ports/URLs without a discovery fallback (read package.json scripts, framework config, env files)
- [ ] External tool dependencies are checked and produce a clear install message if missing

#### G. "When NOT to use"

Reduces over-triggering and protects the context budget of other skills.

- [ ] Body contains an explicit "When NOT to use" or negative-trigger section
- [ ] Each negative case suggests what the model SHOULD do instead

#### H. Delegation antipattern (Claude Code-specific)

A SKILL.md whose body says "use the /foo slash command for the workflow" is broken: it leaves the procedural content in a separate file the skill loader doesn't know about. The skill should either inline the workflow or explicitly reference a markdown file the model is told to read.

- [ ] SKILL.md body contains the workflow OR explicitly directs the model to read a specific reference file (e.g. "Read references/workflow.md")
- [ ] Slash commands and skills do not silently duplicate or split workflow content

#### I. Evals

Without evals, drift on model upgrades is invisible.

- [ ] At least one realistic positive example exists (a prompt that should activate the skill)
- [ ] At least one negative example exists (a prompt that should NOT activate it)
- [ ] If the skill produces structured output, an example of expected output exists

#### J. Tax test

Apply this question to every paragraph in the body: "Would the model get this wrong without this instruction?" If no, the paragraph is tax — flag it.

### Step 3 — Report

For each skill, output:

```
## audit-agent-skill — <relative-path/SKILL.md> (<n> body lines)

Verdict: ship-quality | needs work | rewrite

Critical issues (loader architecture, description, delegation antipattern, missing gotchas):
  - <quoted offending line> — <one-line fix>

Moderate issues (over-triggering, missing Don't/Do pairs, portability):
  - <quoted line> — <fix>

Strengths to keep:
  - <one line per strength>

Top edits in priority order:
  1. <file>:<line> — <change>
  2. <file>:<line> — <change>
  3. <file>:<line> — <change>
```

Then a one-line roll-up across all audited skills:

```
Audited <N> skills: <ship-quality count> ship · <needs-work count> needs work · <rewrite count> rewrite
```

## Operating constraints

- **Read each SKILL.md fully before judging.** Don't score from the description alone.
- **Quote evidence when flagging issues — never paraphrase the offending text.**
- **If a skill scores well in an area, say so explicitly.** Don't only flag negatives.
- **If something looks wrong but you're unsure, say "uncertain — check X" rather than guessing.**
- **Do not make the edits.** Audit only. A fix request after the report is a separate Edit operation.

## Common mistakes

- **Auditing reference files.** Files under `references/`, `scripts/`, `assets/`, or `templates/` are not skills. Skip them — they inherit scope from the parent SKILL.md.
- **Treating PASSes as "nothing to mention".** The user wants the full picture, not just failures. Mention what's working.
- **Scoring rule G as PASS just because there's a heading called "Notes" or "Caveats".** It must be a genuine negative-trigger section that names cases NOT to use.
- **Flagging rule A for length when the description is technically ≤50 words but reads like marketing copy.** The word count is necessary, not sufficient — the language test (engineer-speak, not capability-prose) is the harder bar.
- **Confusing this skill with `review-agent-md`.** `review-agent-md` audits `CLAUDE.md` / `AGENTS.md` files. `audit-agent-skill` audits `SKILL.md` files. They share a vocabulary but the rubrics are different.

## Red flags — stop and re-check

- About to suggest "add a section about X" → that's bloat; this rubric is subtractive hygiene more than additive.
- About to make a generic recommendation ("be more specific") → cite the exact line and propose a concrete replacement, or skip.
- About to auto-edit the file → don't. Report only.
- Scorecard exceeding ~30 lines per skill → trim. Each section = one line + indented FAIL details only.
