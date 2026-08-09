## Task
[1-3 sentences. What and why.]

## Don't
- [prohibition] — [concrete alternative]
- [prohibition] — [concrete alternative]

## Report
[1-2 sentences on what to send back when done.]

Every report carries these two, in this order, before anything else:

- **What this lands** — one plain-language paragraph on what changes for someone using the product. A file-by-file changelog does not satisfy this.
- **Screenshots** — if the change alters rendered output, attach them to the PR with `gh pr comment --body-file` or `gh` attachment before reporting. Say `no rendered-output change` when it does not apply. Do not commit image files to the repo.

## Pointers
- [bare list of paths, URLs, commands — NO prose]
- [absolute path to prose-style.md — always, see below]

<!-- Optional sections below — include only when they earn their keep. -->

## Steps
1. [imperative step]
2. [imperative step]

<!--
COMPOSING NOTES — delete this block from the finished prompt.

Both Report bullets above are REQUIRED. Keep them verbatim; they are not examples.
The screenshot bullet stays even on backend-only work — its "no rendered-output change"
branch is the answer, and deleting the bullet is what makes the question get skipped.

PROSE STYLE is also required whenever the deliverable includes prose a human reads —
a report beyond a status line, a PR body, a design doc, a user-facing artifact. That is
most dispatches. Add to `## Don't`:

  No machine-writing tells in prose deliverables — draft to a file, re-read it against
  the prose-style path in Pointers and cut every tell it lists, then submit
  (e.g. `gh pr create --body-file`).

and put the resolved absolute path to `references/prose-style.md` in `## Pointers`.
Drop both only when the dispatch produces code plus a one-line status and nothing else
a human reads.

REVIEW: code-changing dispatches carry a `## Review` section requiring a multi-round
multi-angle loop (~3 rounds: correctness, design/scope, pathway/CI-DX) before the draft
PR. State in the report which rounds ran and what they used, so the reader does not have
to ask whether review happened.
-->
