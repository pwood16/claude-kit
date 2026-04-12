---
description: Observe runtime behavior (network requests, redirects, errors) in a browser to debug issues — use before reading source code
allowed-tools:
  - Bash(agent-browser:*)
  - Bash(which agent-browser:*)
  - Bash(curl:*)
  - Read
  - Grep
  - Glob
argument-hint: "<url>"
---

# Browser Observe Command

Observe what actually happens at runtime before forming hypotheses. This command captures network requests, redirects, console errors, and navigation events to reveal the real cause of bugs like redirect loops, blank pages, and failed loads.

**Core principle: Observe before theorizing.** Never spend more than 5 minutes on a hypothesis without runtime evidence. A single network request with a 401 status code can pinpoint a bug faster than hours of reading source code.

## Your Task

### 1. Parse Arguments

The `$ARGUMENTS` variable contains a URL: `<url>`

If no URL is provided, ask the user for one.

### 2. Check agent-browser is Available

```bash
which agent-browser
```

If not found, tell the user:
> `agent-browser` is not installed. Install it with:
> ```
> npm install -g agent-browser
> agent-browser install
> ```

### 3. Open the Page with Network Monitoring

Open the page. Network request capture begins automatically on open.

```bash
agent-browser open "$URL"
```

### 4. Wait for Activity to Settle

Wait for network activity to finish, then wait an additional 3 seconds to catch async behavior like delayed redirects, lazy API calls, or client-side navigations that fire after initial load.

```bash
agent-browser wait --load networkidle
agent-browser wait 3000
```

### 5. Capture the Network Sequence

Get all network requests that occurred during page load:

```bash
agent-browser network requests
```

If investigating a specific endpoint or pattern, filter:

```bash
agent-browser network requests --filter "api"
```

### 6. Check for Errors

Capture any console errors and page errors:

```bash
agent-browser errors
agent-browser console
```

### 7. Detect Navigation / Redirects

Check the current URL to see if the page redirected:

```bash
agent-browser get url
```

If the current URL differs from the original `$URL`, a redirect occurred. Note the chain.

For redirect loops, the page may still be navigating. If you suspect a loop:

```bash
agent-browser get url
agent-browser wait 2000
agent-browser get url
```

If the URL keeps changing, you've found a redirect loop. Capture the network requests again to see the full chain:

```bash
agent-browser network requests
```

### 8. Screenshot the Final State

```bash
agent-browser screenshot --annotate
```

Review the screenshot — a blank page, error page, or login page all provide diagnostic information.

### 9. Report What You Observed

Present findings as an ordered sequence of what happened:

```
## Observation Report: $URL

### Request Sequence
1. GET /page → 200
2. GET /api/data → 401
3. Navigation to /sign-in
4. GET /sign-in → 200
5. GET /api/data → 401
6. Navigation to /sign-in (LOOP DETECTED)

### Errors
- Console: "Unauthorized" error from api-client.ts:42
- 401 response on /api/data

### Red Flags
- [x] 4xx/5xx responses: GET /api/data → 401
- [x] Redirect chain: /page → /sign-in → /sign-in (loop)
- [x] Suspicious request: authenticated API call on sign-in page
```

Flag these specific patterns:
- **4xx/5xx responses** — failed requests often reveal the root cause
- **Redirect chains** (>1 redirect) — potential loops
- **Suspicious requests** — e.g., authenticated API calls on a login page, requests that shouldn't happen on the current page
- **Repeated request patterns** — the same request firing multiple times suggests a loop or retry storm

### 10. Form a Hypothesis (Now You Can)

Only after observing, narrow the search:

1. **Grep for the symptom, not the system.** If you saw a redirect to `/sign-in`, grep for ALL code that navigates to `/sign-in` — not just the auth middleware you expect:
   ```bash
   # Search for ALL references to the redirect target
   ```
   Use the Grep tool to search broadly across the codebase.

2. **Grep for the failing endpoint.** If `/api/data` returned 401, find what calls it and what handles the error:
   ```bash
   # Search for the endpoint and its error handling
   ```

3. **Ask "what runs everywhere?"** For bugs that happen on every page, check the root layout, global providers, and components that mount on every route.

4. **Follow the mechanism you observed.** Don't guess — you saw exactly how the bug manifests. Trace that specific code path.

### 11. Close the Browser

```bash
agent-browser close
```

## Server-Side Redirect Fallback

If the issue is a server-side redirect (the page redirects before any JavaScript runs), `curl` can trace the redirect chain faster:

```bash
curl -v -L --max-redirs 10 "$URL" 2>&1 | grep -E "^[<>] (HTTP/|Location:)"
```

This shows each hop in the redirect chain with status codes and Location headers. Use this when:
- The browser observation shows the page arriving already-redirected
- You suspect server-side middleware or reverse proxy redirects
- You want to isolate server-side vs client-side redirect behavior
