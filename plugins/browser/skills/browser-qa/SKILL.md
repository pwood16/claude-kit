---
name: browser-qa
description: Use when you have just built or modified frontend code (HTML, CSS, JSX, TSX, Vue, Svelte) and should verify the result visually, or when the user asks you to check how a page looks
---

# Browser QA Verification

Visually verify your frontend work using `agent-browser` after building or modifying web UI.

## When to Use

- You just created or modified HTML, CSS, JSX, TSX, Vue, or Svelte files
- You changed page layout, styling, or interactive elements
- You built a new web component or page
- The user asks you to check how something looks

## When NOT to Use

- Backend-only changes with no frontend impact
- Config/build changes that don't affect rendered output
- The user explicitly says they'll check it themselves

## Workflow

1. Determine the URL (detect dev server or ask user)
2. Use the `/browser:qa` command to run verification
3. If issues found, fix them and re-verify

Invoke the `/browser:qa` slash command — it contains the full verification workflow.
