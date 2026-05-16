---
description: Scaffold ~/dev/hub/ (operational hub) plus ~/dev/dispatched-head/ and ~/dev/dispatched/ (dispatch siblings) with the default slim layout. Idempotent — safe to re-run.
argument-hint: "(no arguments)"
---

# /hub init

Scaffold the personal operational-control directory layout under `~/dev/`. Run this once per machine before using `/brain`, `/brain-health`, or `/dispatch`.

## What this creates

```
~/dev/
├── hub/
│   ├── brain/
│   │   └── raw/        # pristine source material (often symlinks)
│   ├── research/       # dated investigations
│   ├── decisions/      # ADRs
│   ├── plans/          # implementation plans
│   ├── tasks/          # open action items + dispatched-agent task files
│   └── README.md       # describes the layout
├── dispatched-head/    # canonical clones for dispatch (one per repo)
└── dispatched/         # worktree-mode dispatch workspaces
```

## Workflow

1. Run the bash command below to create every directory. `mkdir -p` is idempotent — re-running this command does not destroy existing content.

   ```bash
   mkdir -p \
     ~/dev/hub/brain/raw \
     ~/dev/hub/research \
     ~/dev/hub/decisions \
     ~/dev/hub/plans \
     ~/dev/hub/tasks \
     ~/dev/dispatched-head \
     ~/dev/dispatched
   ```

2. If `~/dev/hub/README.md` does not exist, write the default README. If it exists, do not overwrite — the user may have customized it.

   Default README content:

   ```markdown
   # hub

   Personal operational-control directory. The skills in the `hub` plugin
   (claude-kit) operate on this tree — see `/brain`, `/brain-health`, `/dispatch`.

   ## Layout

   - `brain/` — AI-maintained per-domain wiki + `INDEX.md`. Never hand-edit;
     regenerate via `/brain`.
   - `brain/raw/` — pristine source material, often symlinks to other repos.
   - `research/` — dated investigations (`YYYY-MM-DD-<slug>.md`).
   - `decisions/` — ADRs.
   - `plans/` — implementation plans.
   - `tasks/` — open action items, dispatched-agent task files.

   ## Dispatch siblings

   `~/dev/dispatched-head/` and `~/dev/dispatched/` live alongside this dir
   (not inside it) so worktrees stay clean of operational metadata.
   ```

3. Report what was created vs. already present. Format:

   ```
   /hub init — scaffolded ~/dev/hub/ + dispatch siblings

   created: <list of newly-created dirs, one per line>
   present: <list of dirs that already existed>
   readme:  <written | preserved (already existed)>

   Next: `/brain` to compile the wiki, or `/dispatch` to hand off work.
   ```

## Rules

- Idempotent. Re-running must not destroy existing content.
- Never write inside an existing `~/dev/hub/README.md` — only write it on first run.
- Do not pre-populate `brain/`, `research/`, etc. with placeholder files. Empty dirs are fine; the brain skill tolerates them.
- Do not touch repos under `~/dev/` that are not at the documented paths above. Limit writes to the paths listed in "What this creates".
