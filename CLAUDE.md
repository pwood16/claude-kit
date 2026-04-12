# Claude Kit

## Session Start

On your first interaction with the user in a new session, run the `/prime` command to familiarize yourself with this project before responding.

## Adding a New Plugin

Two things are required for a plugin to be installable via the marketplace:

### 1. Plugin directory with `.claude-plugin/plugin.json`

```
plugins/<name>/
├── .claude-plugin/
│   └── plugin.json       # name, description, version, author
├── commands/
│   └── command-name.md   # slash commands
├── skills/               # optional — auto-triggered skills
│   └── skill-name/
│       └── SKILL.md
└── README.md
```

`plugin.json` must include a `version` field:

```json
{
  "name": "my-plugin",
  "description": "What it does",
  "version": "1.0.0",
  "author": { "name": "Your Name" }
}
```

### 2. Register in `.claude-plugin/marketplace.json`

The marketplace registry at the repo root is what `claude plugin install` uses for discovery. **If your plugin isn't listed here, it won't be found.** Add an entry to the `plugins` array:

```json
{
  "name": "my-plugin",
  "source": "./plugins/my-plugin",
  "description": "What it does"
}
```

### Install flow

After merging both changes:

```bash
claude plugin marketplace update claude-kit
claude plugin install my-plugin@claude-kit --scope user
```
