# review

Skills for reviewing things — agent-context markdown, documents you want feedback on, and the HTML they produce.

| Skill | Purpose |
|-------|---------|
| `review-agent-md` | Score `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` / `.cursorrules` / Copilot-instructions against a 12-rule rubric (length w/ `@import` math, scope-broadness, Anthropic-excluded content, paired Don't/Do, temporal staleness, etc.). Full-file or diff-only mode. Report-only — no auto-edits. |
| `review-doc` | Turn a markdown draft (RFC, plan, ticket) into a single-file HTML review page with per-section status pills and comments. After the reviewer exports a JSON of their feedback, read it back and apply the comments to the source. |
| `iterate-diagram` | Visually iterate on any HTML file (diagram, dashboard, the review pages `review-doc` produces) via Playwright screenshots — screenshot, show, critique, edit, repeat. |
| `audit-agent-skill` | Rubric one or more `SKILL.md` files against a 10-section best-practices checklist (A–J: description, progressive disclosure, gotchas, anti-rationalization, portability, when-not-to-use, delegation antipattern, evals, tax test). Report-only. |

`review-doc` + `iterate-diagram` pair naturally: generate the HTML review page, then iterate on it visually before sharing.

`review-agent-md` and `audit-agent-skill` are siblings — the first rubrics `CLAUDE.md`/`AGENTS.md`-style agent-context files; the second rubrics `SKILL.md` files for installed agent skills.

## Install

Add via the claude-kit marketplace. Slash commands: `/review-agent-md`, `/review-doc`, `/iterate-diagram`, `/audit-agent-skill`.

For `iterate-diagram`, install Playwright once: `npx playwright install chromium` (preferred) or `npm install -g playwright`.

## Excluded by design

- Skills that own their own rubric (e.g. `superpowers:writing-skills` for `SKILL.md`) — `review-agent-md` defers to those.
- Auto-editing the file under review — `review-agent-md` is report-only. **Do** paste a `Don't` line back and it will suggest a paired `Do`.
