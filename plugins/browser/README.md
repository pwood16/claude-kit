# Browser Plugin

Browser automation for AI agents using [agent-browser](https://github.com/vercel-labs/agent-browser) — Vercel's headless browser CLI optimized for LLM context windows.

## Commands

### `/browser:qa [url]`
QA verify a web page or app. Check that it looks and works correctly after modifications.

- Provide a URL or let it auto-detect your dev server
- Takes annotated screenshots and snapshots interactive elements
- Reports visual issues, broken elements, missing content
- Also available as an auto-triggered skill when you modify frontend code

### `/browser:observe <url>`
Observe runtime behavior to debug issues like redirect loops, blank pages, or unexpected navigations.

- Captures network requests with status codes during page load
- Detects redirect chains and loops
- Reports console errors and page errors
- Guides hypothesis formation based on what was actually observed
- Also available as an auto-triggered skill when debugging runtime behavior

### `/browser:read <url>`
Extract and summarize content from web pages — especially useful for pages that are hard to scrape (Twitter/X, SPAs, auth-gated content).

- Handles JavaScript-heavy pages that `curl`/`WebFetch` can't read
- Scrolls through long content (threads, infinite scroll)
- Presents extracted content in clean, organized format

## Requirements

- `agent-browser` CLI: `npm install -g agent-browser`
- Chrome for Testing: `agent-browser install`

## Installation

```bash
claude plugin install browser@claude-kit --scope user
```
