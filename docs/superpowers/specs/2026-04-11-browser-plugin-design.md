# Browser Plugin Design

A `browser` plugin for claude-kit that uses `agent-browser` (Vercel's headless browser CLI for AI agents) to provide two capabilities: QA verification and content extraction.

## Plugin Structure

```
plugins/browser/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── qa.md          # Slash command for QA verification
│   └── read.md        # Slash command for content extraction
├── skills/
│   └── browser-qa/
│       └── SKILL.md   # Auto-trigger skill for QA verification
└── README.md
```

## Dependencies

- `agent-browser` CLI (installed globally via `npm install -g agent-browser`)
- Chrome for Testing (installed via `agent-browser install`)

## Command: `/browser:qa [url]`

### Purpose

Verify that a web app/page looks and behaves correctly after agent modifications. Available as both a slash command and an auto-triggered skill.

### Usage

- `/browser:qa http://localhost:3000` — explicit URL
- `/browser:qa` — auto-detect dev server URL from project context
- Auto-triggers when agent has built/modified frontend code (HTML, CSS, React, Vue, etc.)

### Workflow

1. Ensure `agent-browser` is available (`which agent-browser`)
2. Open target URL: `agent-browser open <url>`
3. Take annotated screenshot: `agent-browser screenshot --annotate`
4. Snapshot interactive elements: `agent-browser snapshot -i`
5. Evaluate page against expectations — report visual issues, broken elements, missing content
6. If issues found, describe with element refs for easy fixing
7. Close: `agent-browser close`

### Allowed Tools

`Bash(agent-browser:*)`, `Read`, `Glob`

## Command: `/browser:read <url>`

### Purpose

Extract and summarize content from web pages, especially ones that are hard to scrape (SPAs, X/Twitter, auth-gated pages).

### Usage

- `/browser:read https://x.com/user/status/123` — read a Twitter thread
- `/browser:read https://docs.example.com/guide` — read documentation

### Workflow

1. Ensure `agent-browser` is available
2. Open URL: `agent-browser open <url>`
3. Wait for load: `agent-browser wait --load networkidle`
4. Screenshot for visual context: `agent-browser screenshot`
5. Full page snapshot: `agent-browser snapshot`
6. For long pages, scroll and re-snapshot to capture all content
7. Extract key text from relevant elements: `agent-browser get text @ref`
8. Close: `agent-browser close`
9. Present extracted content in a clean, organized summary

### Content-Type Behaviors

- **Twitter/X threads:** scroll through full thread, capture all tweets/replies
- **Articles:** extract title, author, body text, skip nav/ads
- **Documentation:** preserve structure (headings, code blocks)
- Use `--max-output` flag to prevent token bloat on huge pages

### Allowed Tools

`Bash(agent-browser:*)`, `Read`

## Auto-Trigger Skill: browser-qa

The `skills/browser-qa/SKILL.md` skill auto-triggers when an agent has just built or modified frontend code. It runs the same workflow as `/browser:qa` but is initiated by the agent rather than the user.

### Trigger Conditions

- Agent has just created or modified HTML, CSS, JSX, TSX, Vue, or Svelte files
- Agent has changed page layout, styling, or interactive elements
- Agent has built a new web component or page

## Design Decisions

- **Direct CLI approach:** No wrapper scripts. Agent calls `agent-browser` CLI commands directly via Bash, matching the pattern used by other claude-kit plugins.
- **One plugin, two commands:** Both capabilities share the same underlying tool, so they belong together.
- **Snapshot + Refs:** Leverages agent-browser's core innovation — compact element references (`@e1`, `@e2`) that save ~93% context window compared to raw HTML/accessibility trees.
- **Slash command + auto-trigger for QA:** QA is most valuable when agents self-verify, but manual triggering is also useful. Content extraction is always explicit (URL required).
