# Claude Kit

A collection of helpful utilities and enhancements for Claude Code.

## Features

### [Session Tracker](docs/session-tracker.md)
Automatically capture and browse summaries of your cleared sessions. When you run `/clear`, this plugin saves a searchable summary of what you accomplished.

- Captures session metadata and files touched
- Generates concise title and summary via LLM
- Browse with `/claude-kit:prior-sessions`

See [docs/session-tracker.md](docs/session-tracker.md) for installation and usage.

### [Statusline](scripts/README.md)
Enhanced statusline with comprehensive git status indicators, token tracking, and color-coded status.

Example: `[Sonnet 4.5 (1M context)] claude-kit:main [!1 ⚠] | 49,221 session tokens`

See [scripts/README.md](scripts/README.md) for installation and configuration details.

## Installation

```bash
# Install as a plugin (globally)
claude plugin install /path/to/claude-kit --scope user

# Or for development/testing
claude --plugin-dir /path/to/claude-kit
```

## Resources

- [Claude Code Documentation](https://code.claude.com/docs)
