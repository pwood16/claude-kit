# Claude Kit

A marketplace of productivity plugins for Claude Code.

## Plugins

### [Spawn](plugins/spawn)
Spawn Claude agents in git worktrees for parallel development work.

- `/spawn:wt-agent <name> [prompt]` - Create a worktree and spawn a new agent with optional prompt
- `/spawn:plan-to-prd [plan-file] [--out output.json]` - Convert a plan into a ralph-loop PRD JSON file
- Supports interactive mode (`--interactive`) for REPL-style development
- Supports print mode (`--print`) to output paths without spawning terminal
- Each agent works in isolation with full git history
- Worktrees are created in `.wt-agents/` directory (can be gitignored)

See [plugins/spawn](plugins/spawn) for details.

### [GitHub Workflow (gh)](plugins/gh)
GitHub branch and PR workflow automation commands.

- `/gh:load-pr [branch-or-pr-number]` - Fetch, checkout, and load PR context for review
- `/gh:pr-draft` - Smart commit, push, and create draft PR with AI-generated description

See [plugins/gh](plugins/gh) for details.

### [Excalidraw](plugins/excalidraw)
Create diagrams from text descriptions and export to SVG.

- `/excalidraw:create <name> <description>` - Generate `.excalidraw` and `.svg` files from a description
- Supports architecture diagrams, flowcharts, entity diagrams, network diagrams, and more
- Output saved to `docs/diagrams/`

See [plugins/excalidraw](plugins/excalidraw) for details.

### [Hub](plugins/hub)
Personal operational-control hub at `~/dev/hub/` — a single place for notes, plans, and an AI-compiled per-domain wiki.

- `/hub:init` - Idempotent scaffolder for `~/dev/hub/` and dispatch sibling dirs
- `/hub:brain [domain]` - Compile per-domain wiki at `~/dev/hub/brain/<domain>.md` from hub sources
- `/hub:brain-health` - Diff the wiki against live sources (file mtimes, `gh`, optional MCP) and flag stale or missing content
- `/hub:dispatch [path-or-ticket]` - Hand off work to a background Claude in a tmux session; worktree mode default at `~/dev/dispatched/<slug>/<repo>/`
- Dynamic base-branch detection — no hardcoded per-repo branch map

See [plugins/hub](plugins/hub) for details.

### [Review](plugins/review)
Review-oriented skills — both for human documents and the markdown files that configure agents.

- `/review:review-agent-md [path]` - Rubric a `CLAUDE.md` / `AGENTS.md` / `.cursorrules` / Copilot-instructions file against 9 best-practice rules
- `/review:audit-agent-skill [path]` - Rubric `SKILL.md` files against a 10-section best-practices rubric (A–J)
- `/review:review-doc <path>` - Generate an HTML review page from a markdown draft, then apply reviewer-exported JSON feedback back to the source
- `/review:iterate-diagram <html-file>` - Visually iterate on any HTML file (diagrams, dashboards, review pages) via Playwright screenshots
- Pairs naturally with `/hub` for compiling and reviewing personal docs

See [plugins/review](plugins/review) for details.

## Installation

### Add the Marketplace

```bash
# Add the claude-kit marketplace from GitHub
claude plugin marketplace add pwood16/claude-kit
```

### Install Plugins

```bash
# Pattern: Install any plugin globally (available in all projects)
claude plugin install <plugin-name>@claude-kit --scope user

# Or install for a specific project only
claude plugin install <plugin-name>@claude-kit --scope project

# Example: Install the spawn plugin
claude plugin install spawn@claude-kit --scope user
```

## Development

To test plugins without installing via the marketplace:

```bash
# Pattern: Test any plugin locally
claude --plugin-dir /path/to/claude-kit/plugins/<plugin-name>

# Example: Test the spawn plugin
claude --plugin-dir /path/to/claude-kit/plugins/spawn
```

## Resources

- [Claude Code Documentation](https://code.claude.com/docs)
