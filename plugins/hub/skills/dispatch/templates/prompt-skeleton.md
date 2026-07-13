## Task
[1-3 sentences. What and why.]

## Don't
- [prohibition] — [concrete alternative]
- [prohibition] — [concrete alternative]

## Review
[Required for any code-changing dispatch. Default expectation:
- After local checks are green (lint/test/clippy/fmt, plus the codebase's pre-push suite), run a multi-angle review loop.
- Spawn parallel reviewer subagents covering at least: correctness, design/scope, pathway/integration (plus security if relevant). Use the codebase's review skill if one exists (e.g. `/review`, `/security-review`).
- Iterate until reviewers converge with no Important findings — typically ~3 rounds.
- Address each round's findings in a follow-up commit or fold-in.
- Document round outcomes briefly in the Report (rounds run, what each flagged, what was fixed).]

## Report
[1-2 sentences on what to send back when done. For code-changing dispatches include: branch + draft PR URL, summary of changes, review-round summary.]

<!-- Optional sections below — include only when they earn their keep. -->

## Pointers
- [bare list of paths, URLs, commands — NO prose]

## Steps
1. [imperative step]
2. [imperative step]
