---
name: browser-qa
description: Use after frontend changes that affect what a user sees in a browser (layout, styling, new components, interactive flows). Captures screenshots plus a live interactive-element snapshot to verify visually. Skip for internal refactors that don't change rendered output.
---

# Browser QA Verification

Visually verify frontend work using `agent-browser`. The model already knows what HTML looks like; this skill exists because rendering, async data, and interaction state diverge from what the source code suggests.

## When to use

- A change affects rendered output: page structure, styling, copy, components, routing, interactive widgets
- A bug report describes something visual ("the modal is cut off", "the button doesn't respond")
- The user asks you to check how a page looks or behaves

## When NOT to use

| Don't | Do instead |
|---|---|
| Backend-only change | Verify the API contract still matches what the frontend consumes (read the consuming component) |
| Build/config change with no UI impact | Verify the build artifact (compiled output, generated HTML, bundle) |
| User said they'll check it themselves | Offer a baseline screenshot only if useful for a future comparison |
| Pure logic refactor (extracted hook, renamed util) with no rendered diff | Run the test suite; visual QA adds no signal |
| Dev server isn't running and won't start | Stop and ask the user — don't QA a connection-error page and report "broken" |

## Gotchas

These are the failure modes that show up when this skill is run carelessly. They are the actual reason this skill exists.

- **Screenshot before `networkidle`.** Capturing during initial paint shows spinners, half-loaded fonts, or skeleton states — not the real UI. Always `wait --load networkidle` first, and for animation-heavy pages add a short fixed wait after.
- **"Looks fine" without exercising interaction.** A static screenshot doesn't prove buttons work, forms validate, or modals open. If the change touched interactive elements, click at least one and re-screenshot.
- **Default viewport hides the bug.** If the report mentions mobile, tablet, or "responsive", set the viewport before screenshotting. Desktop view will silently pass on a mobile-only bug.
- **Snapshot ≠ screenshot.** The interactive snapshot shows what the DOM thinks exists; the screenshot shows what the user actually sees. CSS bugs (overlap, clipping, hidden overflow) are invisible in the snapshot. Use both.
- **Console errors ignored.** A page can render perfectly and still be broken (failed analytics, hydration warnings, uncaught promises). Always check console output as part of QA, not just visuals.
- **QA before the dev tool finishes rebuilding.** With HMR or watch builds, screenshotting immediately after editing a file may capture the pre-change state. Reload, then `wait --load networkidle`.
- **Connection-error page reported as "broken UI".** A blank page or `ERR_CONNECTION_REFUSED` means the dev server isn't running, not that the feature is broken. Check the URL responds before claiming a defect.
- **Forgetting `agent-browser close`.** Leaves an orphaned Chrome process. Always close at the end, even on failure.

## Anti-rationalization

The model will be tempted to skip this skill. Common excuses and what to do instead:

- *"The change is small, the diff looks right."* — Visual rendering is not derivable from the diff. Even one-line CSS changes can cascade. Verify.
- *"I already checked the interactive snapshot."* — The snapshot doesn't show layout, color, overflow, or z-index bugs. Take the screenshot too.
- *"There's no dev server running, I'll skip."* — Ask the user how to start it. Don't claim work is done because verification was inconvenient.

## Workflow

### 1. Resolve the URL

If the user passed a URL, use it. Otherwise discover (in order):
- `package.json` `scripts.dev` / `scripts.start` — extract the port if specified
- Framework config: `next.config.*`, `vite.config.*`, `astro.config.*`, `nuxt.config.*`
- `.env`, `.env.local` for `PORT=`
- Fallback defaults to try in order: `http://localhost:3000`, `http://localhost:5173`, `http://localhost:8080`
- If none responds, ask the user

### 2. Verify `agent-browser` is installed

```bash
which agent-browser
```

If missing:
> `agent-browser` is not installed. Install with: `npm install -g agent-browser && agent-browser install`

### 3. Open the page and wait for settle

```bash
agent-browser open "$URL"
agent-browser wait --load networkidle
```

For pages with entry animations or delayed data, add `agent-browser wait 1000`.

### 4. Set viewport if the change is responsive

Skip for desktop-only changes.

```bash
agent-browser set viewport 375 812   # iPhone-ish
agent-browser set viewport 768 1024  # tablet
```

### 5. Capture evidence

```bash
agent-browser screenshot --annotate
agent-browser snapshot -i
agent-browser console
agent-browser errors
```

The annotated screenshot labels interactive elements with refs (`@e1`, `@e2`, …) so the snapshot output and screenshot can be cross-referenced.

### 6. Exercise interactive elements (if the change touched them)

For each interactive element relevant to the change:

```bash
agent-browser click @e<ref>
agent-browser wait --load networkidle
agent-browser screenshot --annotate
```

Verify the result matches expectation (modal opened, form submitted, navigation occurred, etc.).

### 7. Close the browser

```bash
agent-browser close
```

### 8. Report

Use this structure:

```
## QA Report: <URL>

### Verified
- <thing checked>: <pass/fail with one-line reason>
- ...

### Issues
- <issue>: <what's wrong, where it is (e.g. @e3 in header), evidence>
- ...

### Console / errors
- <any non-empty output>

### Verdict
<pass | fails listed above>
```

If everything passes, the Issues section is "(none)" and the Verdict is "pass — all checks succeeded".

## Evals

See `references/evals.md` for positive and negative trigger examples and a sample expected report.
