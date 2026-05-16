# hub

Personal operational-control plugin. Treats `~/dev/hub/` as your second-brain
workspace and gives Claude two skills for keeping it useful:

| Skill | Purpose |
|-------|---------|
| `brain` | Compile `~/dev/hub/brain/<domain>.md` wiki files from everything under `~/dev/hub/` (raw notes, dated investigations, synced repo activity). One file per topic — regenerated via `/brain`, not hand-edited. |
| `brain-health` | Diff the wiki against live sources (GitHub activity, file mtimes, anything you've configured) and report stale topics, missing topics, resolved questions. |
| `dispatch` | Hand off work to a background Claude in a tmux session. Worktree mode (default) at `~/dev/dispatched/<slug>/<repo>/`; own-folder mode at `~/dev/<TICKET>/<repo>/` for multi-week work. |

## Directory layout the skills expect

```
~/dev/
├── hub/
│   ├── brain/                 # AI-maintained wiki — one .md per domain, plus INDEX.md
│   │   └── raw/               # Pristine source material, often symlinked from other repos
│   ├── research/              # Dated investigations
│   ├── decisions/             # ADRs
│   ├── plans/                 # Implementation plans / drafts
│   └── tasks/                 # Open action items, dispatched-agent task files
├── dispatched-head/           # Canonical clones used by /dispatch (sibling of hub/)
└── dispatched/                # Worktree-mode dispatch workspaces (sibling of hub/)
```

The brain skills tolerate missing subdirs — they skip silently. Add what you
actually use.

## Install

Add the plugin via the claude-kit marketplace, then **run `/hub init` once** to
scaffold the directory layout above. After that: `/brain`, `/brain-health`, `/dispatch`.
