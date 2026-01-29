# Claude Kit

A marketplace of productivity plugins for Claude Code.

## Plugins

### [Spawn](plugins/spawn)
Spawn Claude agents in git worktrees for parallel development work.

- `/spawn:wt-agent <name> [prompt]` - Create a worktree and spawn a new agent with optional prompt
- Supports interactive mode (`--interactive`) for REPL-style development
- Supports print mode (`--print`) to output paths without spawning terminal
- Each agent works in isolation with full git history

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
