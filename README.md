# Claude Kit

A marketplace of productivity plugins for Claude Code.

## Plugins

### [Prior Session](plugins/prior-session)
Automatically capture and browse summaries of your cleared sessions. When you run `/clear`, this plugin saves a searchable summary of what you accomplished.

- Captures session metadata and files touched
- Generates concise title and summary via LLM
- Browse with `/prior-session:browse`

See [plugins/prior-session](plugins/prior-session) for details.

### [GitHub Workflow (gh)](plugins/gh)
GitHub branch and PR workflow automation commands.

- `/gh:load-pr [branch-or-pr-number]` - Fetch, checkout, and load PR context for review
- `/gh:pr-draft` - Smart commit, push, and create draft PR with AI-generated description

See [plugins/gh](plugins/gh) for details.

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

# Example: Install the gh plugin
claude plugin install gh@claude-kit --scope user
```

## Development

To test plugins without installing via the marketplace:

```bash
# Pattern: Test any plugin locally
claude --plugin-dir /path/to/claude-kit/plugins/<plugin-name>

# Example: Test the gh plugin
claude --plugin-dir /path/to/claude-kit/plugins/gh
```

## Resources

- [Claude Code Documentation](https://code.claude.com/docs)
