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
# Add the claude-kit marketplace
claude plugin marketplace add /path/to/claude-kit/.claude-plugin/marketplace.json

# Or add from GitHub (once published)
claude plugin marketplace add your-username/claude-kit
```

### Install Plugins

```bash
# Install the prior-session plugin globally
claude plugin install prior-session@claude-kit --scope user

# Or install for a specific project only
claude plugin install prior-session@claude-kit --scope project
```

## Development

To test plugins without installing via the marketplace:

```bash
# Test a specific plugin
claude --plugin-dir /path/to/claude-kit/plugins/prior-session
```

## Resources

- [Claude Code Documentation](https://code.claude.com/docs)
