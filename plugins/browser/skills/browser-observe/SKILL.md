---
name: browser-observe
description: Use when debugging runtime behavior — redirect loops, blank pages, unexpected navigations, page load failures, or any bug where the symptom is about what happens at runtime rather than what the code says
---

# Browser Observation for Debugging

Observe what actually happens at runtime before forming hypotheses or reading source code. Network requests, redirects, and console errors reveal root causes faster than code archaeology.

## When to Use

- Debugging redirect loops or unexpected navigations
- Investigating "blank page" or "page won't load" issues
- Any bug where the symptom is about runtime behavior (not static code)
- You've spent more than 5 minutes reading source code for a runtime bug without progress
- The user reports behavior that doesn't match what the code seems to do

## When NOT to Use

- The bug is clearly in static code (syntax error, wrong variable name)
- Build/compile errors — no runtime to observe
- Backend-only bugs with no browser component
- The user has already provided network/console output

## Workflow

1. **Stop reading source code** — you're here because observation is faster
2. Use the `/browser:observe` command with the affected URL
3. The observation report tells you exactly where to look in the code
4. Only then read the specific files the observation points to

Invoke the `/browser:observe` slash command — it contains the full observation and diagnosis workflow.
