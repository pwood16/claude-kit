---
description: Generate an HTML review page from a markdown doc (plan, RFC, ticket draft), or read back exported reviewer feedback and apply it to the source.
argument-hint: "<path-to-markdown-or-feedback-json>"
---

Invoke the `review-doc` skill (from the `review` plugin) with arguments: `$ARGUMENTS`.

The skill has two workflows — Generate and Read-back. Pick based on file extension and the user's wording:

- `.md` source, or "make a review page" / "send this for review" → Generate
- `*-review-comments.json`, or "read my feedback" / "apply the review comments" → Read-back

If `$ARGUMENTS` is empty, ask the user which workflow they want and what file to operate on.
