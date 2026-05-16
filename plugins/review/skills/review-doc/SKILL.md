---
name: review-doc
description: Use when the user wants to generate an HTML review page from a markdown doc (/review-doc, "make a review for X") or apply exported reviewer feedback back to the source ("read my feedback", "apply the review comments", or pointing at a *-review-comments.json file).
---

# review-doc

Turn a markdown doc (plan, RFC, ticket draft) into a single-file HTML review page. Reviewer status-pills and comments each section in a browser, exports JSON, then this skill reads the JSON back and applies the feedback to the source markdown.

## Two workflows

| User says | Workflow |
|-----------|----------|
| `/review-doc <path>`, "make a review page for X", "I need to send this for review" | **Generate** |
| "read my feedback", "I'm done reviewing", "apply the review comments", points at `*-review-comments.json` | **Read back** |

State persists at `~/.claude/state/review-doc/.state.json` — write it after generate, read it on read-back.

```json
{
  "last": {
    "doc_name": "<kebab-case>",
    "source_path": "/abs/path/source.md",
    "html_path": "/abs/path/source-review.html",
    "json_path": "/Users/<user>/Downloads/<doc-name>-review-comments.json"
  }
}
```

## Workflow: Generate

1. Read the source markdown end-to-end. Note its structure.
2. Pick reviewable sections — usually top-level `##` blocks, or `---`-separated blocks. Skip pure context/preamble (recap, brain refs).
3. Assign each reviewable section a **lane** from the decision table below.
4. Read `templates/section-snippets.md` for the HTML fragments. Compose the body in this order:
   - **Recap** (`section` — not reviewable). Brief — link/anchor, don't restate the source verbatim.
   - **Anchor list** (inside recap).
   - **Diagram** (only if the source has sequencing/lifecycle info worth a picture — hand-roll SVG, no CDN).
   - Group label: `<h2 class="group-label">…</h2>`
   - **Reviewable cards** — one per section, with `<div class="review-block" data-ticket="<ID>" data-reviewable="true"></div>`.
   - **Open questions** (only if the source has them — comment-only, no status pills).
   - **Updates table** (only if the source has an "existing items to update" section).
   - **General notes** (always last — single `<textarea class="comment" data-ticket="general">`).
5. Read `templates/base.html`. Substitute placeholders:
   - `{{HEADER_TITLE}}` — derive from source H1.
   - `{{HEADER_SUBTITLE}}` — `Draft <date> · For <audience> alignment` or similar one-liner.
   - `{{DOC_NAME}}` — source filename without `.md` (kebab-case).
   - `{{SOURCE_PATH}}` — absolute path to source.
   - `{{REVIEWER}}` — `$USER` (or `Reviewer` if unset).
   - `{{BODY}}` — the composed body from step 4.
6. Write to `<source-dir>/<source-name>-review.html`.
7. Update `~/.claude/state/review-doc/.state.json` with the new `last` entry.
8. Tell the user the path and suggest `open <path>`. One sentence.

### Lane decision table

| Source semantics | Lane class | Badge palette | When to use |
|------------------|------------|---------------|-------------|
| Schema, migration, infra, "foundation" | `lane-foundation` | `badge-blue` | Backend/data-layer tickets that unblock everything |
| Read path, integration, view, API composition | `lane-composition` | `badge-purple` | Things that read across systems |
| UI, frontend, admin surface | `lane-ui` | `badge-amber` | User-facing rendering |
| Stretch, optional, risky | `lane-stretch` | `badge-red` | Nice-to-haves and experiments |
| Conditional, pending stakeholder | `lane-pending` | `badge-amber` dashed | Awaiting product / design decision |
| Generic, default | `lane-neutral` | `badge-gray` | Nothing else fits |

If the source doesn't categorize cleanly, use `lane-neutral` — don't invent lanes.

### Section IDs

Use short, stable IDs derived from the source: `A`, `B`, `C` for lettered sections; `q1`, `q2` for questions; `updates` for the updates table; `general` for the final textarea. The ID is the localStorage key and the JSON key — keep it short.

## Workflow: Read back

1. Find the JSON:
   - First choice: `~/.claude/state/review-doc/.state.json` → `last.json_path`.
   - Fallback: `ls ~/Downloads/*-review-comments.json | head -1` (most recent).
   - If user pasted a path, use that.
2. Read the JSON. Read the source markdown (`source` field from JSON, or `last.source_path`).
3. **Synthesize** — not summarize. Group the feedback:
   - Sections marked `looks-good` with no comment → skip.
   - Sections with `needs-changes` / `needs-discussion` / a comment → action items.
   - `general` → cross-cutting notes (often "make it more concise").
4. State the proposed changes in 3-6 bullets and **ask before applying** if any are structural rewrites (deleting questions, restructuring sections, changing schemas). Trivial wording fixes can proceed without asking.
5. Apply via `Edit` to the source markdown. Default to concise rewrites — if the reviewer says "too verbose", actually cut words.
6. Flag downstream docs that should follow. Check `brain/` for files referenced by the source (look for `brain/<name>.md` mentions); list them but don't auto-edit unless asked.

## Don't / Do

| Don't | Do |
|-------|----|
| Generate a 250-line HTML for a 50-line markdown | Match the source's visual weight — small doc = small HTML |
| Restate every paragraph in the HTML | Pull just enough so the reviewer doesn't need the source open |
| Add status pills to context paragraphs or recaps | Reserve `data-reviewable="true"` for actual decisions to review |
| Pull in Mermaid, D3, or any CDN | Hand-roll SVG for diagrams; everything inline |
| Skip the clipboard fallback | Keep `showCopyFallback()` — `file://` blocks `navigator.clipboard` in most browsers |
| Leave comments in struck-through state after a "remove Q5" request | Actually delete the content from the source markdown |
| Auto-rewrite when feedback says "discuss with <person>" | That's a discussion item, not a change — flag it, don't edit |
| Edit `brain/` files reflexively after a source edit | Mention them as downstream candidates, ask before editing |

## Quick reference

```bash
# After generate
open /path/to/<doc-name>-review.html

# After reviewer exports JSON
ls -t ~/Downloads/*-review-comments.json | head -1

# State file
~/.claude/state/review-doc/.state.json
```

## Reference files

- `templates/base.html` — full HTML scaffold with inline CSS/JS and `{{...}}` placeholders. Self-contained, works from `file://`.
- `templates/section-snippets.md` — HTML fragments for each section type. Compose `{{BODY}}` from these.
- `examples/feedback.json` — sample reviewer-exported JSON. Useful for sanity-checking the read-back workflow before running it on real feedback.
