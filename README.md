# Claude Kit

A collection of helpful utilities and enhancements for Claude Code.

## Features

### [Prior Sessions](docs/prior-sessions.md)
Automatically capture and browse summaries of your cleared sessions. When you run `/clear`, this plugin saves a searchable summary of what you accomplished.

- Captures session metadata and files touched
- Generates concise title and summary via LLM
- Browse with `/claude-kit:prior-sessions`

See [docs/prior-sessions.md](docs/prior-sessions.md) for details.

### [Statusline](scripts/README.md)
Enhanced statusline with comprehensive git status indicators, token tracking, and color-coded status.

Example: `[Sonnet 4.5 (1M context)] claude-kit:main [!1 ⚠] | 49,221 session tokens`

See [scripts/README.md](scripts/README.md) for installation and configuration details.

## Installation

```bash
# Install globally (available in all projects)
claude plugin install /path/to/claude-kit --scope user

# Or install for a specific project only
claude plugin install /path/to/claude-kit --scope project
```

## Development

To test the plugin without installing:

```bash
claude --plugin-dir /path/to/claude-kit
```

### Test Fixtures

The `test/fixtures/` directory contains sample SessionEnd hook data for testing the prior sessions hook without running `/clear`:

```bash
# Test the hook script with fixture data
cat test/fixtures/sessionend-clear-normal.json | ./hooks-handlers/on-clear.sh
```

See [test/README.md](test/README.md) for details on capturing new fixtures.

## Resources

- [Claude Code Documentation](https://code.claude.com/docs)
