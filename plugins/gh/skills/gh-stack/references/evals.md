# gh-stack evals

Use these to verify the skill activates correctly and drives `gh stack` non-interactively.
Re-run on every model upgrade, skill edit, or gh-stack extension update (public preview —
the surface can move).

## Should activate

1. *"Split this auth work into a stack of PRs — schema first, then the API, then the UI."*
2. *"PR #42 is the middle of a stack; the bottom PR just merged. Get everything retargeted."*
3. *"Add another layer on top of the current stack for the integration tests."*
4. *"gh stack sync said 'Sync aborted' — what now?"*
5. *(A stack is checked out)* "Commit this fix to the layer that owns validation, then update the stack."*

For each, the skill should fire and the agent should use `gh stack` commands with the
non-interactive flags (`view --json`, `submit --auto`, `merge <target> --yes`), never the
bare TUI forms.

## Should NOT activate

1. *"Open a PR for this branch."* — Single ordinary PR; use `gh pr create`.
2. *"These three fixes are unrelated — get them each up for review."* — Independent changes;
   separate PRs against the trunk.
3. *"Rebase my feature branch onto main."* — Plain `git rebase`; no stack involved.
4. *"Review the stack of papers in this folder."* — Not a PR stack.
5. *"Merge PR #7."* — A standalone PR merges with `gh pr merge`.

## Sample expected behavior

For eval 1, the transcript should contain, in order:

```
gh stack init auth/schema          # or repo-convention branch names
git add … && git commit -m "…"
gh stack add auth/api
git add … && git commit -m "…"
gh stack add auth/ui
git add … && git commit -m "…"
gh stack submit --auto
gh stack view --json               # confirm branches, bases, PR numbers
```

## Failure modes to watch for in eval review

- Agent runs `gh stack view`, `submit`, `merge`, or `checkout` without the non-interactive
  flags and hangs in a TUI (gotcha table ignored)
- Agent hand-rolls stacking with `git rebase --update-refs` + `gh pr create --base` instead
  of the extension
- Agent uses `gh pr merge` on a stacked PR
- Skill fires on independent, order-free changes without questioning the coupling
  ("When to stack" ignored)
- Agent parses stderr status text instead of branching on exit codes
