---
name: browser-observe
description: Use when debugging runtime browser behavior — redirect loops, blank pages, unexpected navigations, page-load failures, or any bug whose symptom is what happens at runtime rather than what the code says. Captures network requests, console errors, and final URL before any source-code reading.
---

# Browser Observation for Debugging

Observe what actually happens at runtime *before* forming a hypothesis. A single 401 in the network log can pinpoint a bug faster than an hour of source-code reading.

**Core principle: observe before theorizing.** Never spend more than 5 minutes hypothesizing about a runtime bug without runtime evidence.

## When to use

- Redirect loops or unexpected navigations
- "Blank page" / "page won't load" / "stuck loading"
- Behavior that contradicts what the source code seems to do
- You've been reading source for >5 minutes on a runtime bug with no progress
- Any symptom describing *what happens* in the browser

## When NOT to use

| Don't | Do instead |
|---|---|
| Bug is clearly in static code (syntax error, undefined variable, type error) | Read the file at the error location; observation adds nothing |
| Build or compile errors | Read the build output — there's no runtime to observe |
| Backend-only bug with no browser involvement | Inspect server logs, API responses, or DB state directly |
| User already pasted network/console output | Use what they gave you; don't re-observe |
| You've already observed once and have a hypothesis | Test the hypothesis in code; don't re-observe to confirm a hunch |

## Gotchas

- **Stop reading source code.** If you're invoking this skill, observation is the faster path. Resist the urge to "just check one more file" first.
- **`networkidle` isn't the end.** Async redirects, lazy API calls, and client-side route changes can fire seconds after initial load. Add a fixed wait after `networkidle`.
- **JS-driven vs server-side redirects look different.** A 302 in the network log is server-side. A `Navigation to /sign-in` event with no preceding 3xx is client-side (router push, `window.location =`). The fix lives in different code.
- **Server-side redirects may complete before the browser sees them.** If `agent-browser` reports the page already at the destination, the chain happened pre-JS. Use `curl -v -L` to trace it.
- **Filter the network log when there's noise.** A page making 80 analytics requests will bury the one 401 that matters. `agent-browser network requests --filter "api"` or filter on path fragments.
- **`errors` and `console` are different signals.** `errors` captures uncaught exceptions and page errors. `console` captures `console.log/warn/error`. Bugs hide in both.
- **Repeated identical requests = loop or retry storm.** If the same URL fires 5+ times, that's the bug, even if each individual response is 200.
- **Closing the browser before capturing data discards it.** Capture network/console/errors *before* `agent-browser close`.
- **Re-running observation can mask the bug.** Some bugs (cache, cookies, session state) only fire on the first navigation of a session. If you re-run and the bug is gone, suspect state — not "fixed".

## Anti-rationalization

- *"I think I know what's wrong, I'll just patch it."* — You don't know yet. Observe first; the network log is faster than reading.
- *"The bug is obvious from the code."* — If it were, you wouldn't be debugging. Runtime contradicts code.
- *"Observation takes too long."* — One page load. The alternative is opening 12 source files to chase a hypothesis that the network log would have falsified in 30 seconds.
- *"I already observed once, this run will be the same."* — If you've changed the code since, re-observe to confirm. Don't assume.

## Workflow

### 1. Confirm `agent-browser` is installed

```bash
which agent-browser
```

If missing:
> `agent-browser` is not installed. Install with: `npm install -g agent-browser && agent-browser install`

### 2. Open the page (network capture starts automatically)

```bash
agent-browser open "$URL"
```

### 3. Wait for activity to settle, plus async tail

```bash
agent-browser wait --load networkidle
agent-browser wait 3000
```

The 3-second tail catches delayed redirects and lazy calls.

### 4. Capture the request sequence

```bash
agent-browser network requests
```

If noisy, filter:

```bash
agent-browser network requests --filter "api"
```

### 5. Capture errors and console

```bash
agent-browser errors
agent-browser console
```

### 6. Check current URL for redirects

```bash
agent-browser get url
```

If different from `$URL`, a redirect happened. For suspected loops, sample twice with a delay:

```bash
agent-browser get url
agent-browser wait 2000
agent-browser get url
```

URL still changing → loop. Re-capture network requests to see the full chain.

### 7. Screenshot the final state

```bash
agent-browser screenshot --annotate
```

A blank page, error page, or login page each carry diagnostic signal.

### 8. Close the browser

```bash
agent-browser close
```

### 9. Report what you observed

Use this structure:

```
## Observation Report: <URL>

### Request Sequence
1. <METHOD> <path> → <status>
2. ...

### Errors
- Console: <message> (source if available)
- Page errors: <message>

### Final URL
<current URL — note if it differs from the requested URL or kept changing>

### Red Flags
- [ ] 4xx/5xx responses
- [ ] Redirect chain (>1 hop)
- [ ] Suspicious request (e.g. authenticated API call on a sign-in page)
- [ ] Repeated identical requests (loop / retry storm)
```

Check each red-flag box with the supporting evidence.

### 10. Form a hypothesis from what you observed

Only now read source. Narrow the search using the symptom, not the system you suspect:

- Saw a redirect to `/sign-in`? Grep for *all* code that routes there — middleware, guards, client effects. Don't pre-narrow to "the auth code".
- Saw a 401 from `/api/data`? Find what calls it AND what handles its error.
- Bug appears on every page? Look at the root layout, providers, and global middleware — the things that run everywhere.
- Follow the mechanism you observed. You saw exactly how the bug manifests; trace that code path, not the one you assumed.

## Server-side redirect fallback

When the browser arrives already-redirected, `curl` traces the chain:

```bash
curl -v -L --max-redirs 10 "$URL" 2>&1 | grep -E "^[<>] (HTTP/|Location:)"
```

Use when:
- The browser observation shows the page already at the destination
- You suspect server-side middleware, reverse proxy, or framework-level redirects
- You want to isolate server-side vs client-side redirect behavior

## Evals

See `references/evals.md` for positive and negative trigger examples and a sample expected report.
