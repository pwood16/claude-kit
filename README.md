# Claude Kit

A marketplace of productivity plugins for Claude Code.

## Plugins

### [Prior Session](plugins/prior-session)
Automatically capture and browse summaries of your cleared sessions. When you run `/clear`, this plugin saves a searchable summary of what you accomplished.

- Captures session metadata and files touched
- Generates concise title and summary via LLM
- Browse with `/prior-session:browse`

See [plugins/prior-session](plugins/prior-session) for details.

## Installation

### Add the Marketplace

```bash
# Add the claude-kit marketplace from GitHub
claude plugin marketplace add pwood16/claude-kit
```

### Install Plugins

```bash
# Install the prior-session plugin globally (available in all projects)
claude plugin install prior-session@claude-kit --scope user

# Or install for a specific project only
claude plugin install prior-session@claude-kit --scope project
```

**Note**: This is a private repository. You'll need SSH access configured to install the marketplace.

## Development

To test plugins without installing via the marketplace:

```bash
# Test a specific plugin
claude --plugin-dir /path/to/claude-kit/plugins/prior-session
```

## Resources

- [Claude Code Documentation](https://code.claude.com/docs)
