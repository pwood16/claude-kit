---
description: QA verify a web page or app using agent-browser — check that it looks and works correctly
allowed-tools:
  - Bash(agent-browser:*)
  - Bash(which agent-browser:*)
  - Read
  - Glob
argument-hint: "[url]"
---

# Browser QA Command

Visually verify that a web page or app looks and behaves correctly. Use after building or modifying frontend code.

## Your Task

### 1. Parse Arguments

The `$ARGUMENTS` variable may contain a URL: `[url]`

**If URL provided:** Use it directly.

**If no URL provided:** Auto-detect from project context:
- Check for running dev servers (look for `package.json` scripts like `dev`, `start`)
- Common defaults: `http://localhost:3000`, `http://localhost:5173`, `http://localhost:8080`
- Check for recent terminal output mentioning a local URL
- If unable to detect, ask the user

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

### 3. Open the Page

```bash
agent-browser open "$URL"
```

### 4. Wait for Load

```bash
agent-browser wait --load networkidle
```

### 5. Take Annotated Screenshot

```bash
agent-browser screenshot --annotate
```

The annotated screenshot labels interactive elements, making it easy to see what's on the page.

### 6. Snapshot Interactive Elements

```bash
agent-browser snapshot -i
```

This returns only interactive elements (buttons, links, inputs, etc.) with compact refs.

### 7. Evaluate the Page

Review the screenshot and snapshot against what was expected. Check for:

- **Layout:** Does the page structure match the design intent?
- **Content:** Is all expected text/data present?
- **Interactive elements:** Are buttons, forms, links present and properly labeled?
- **Visual issues:** Overlapping elements, broken images, missing styles, misalignment
- **Responsiveness:** If relevant, check different viewport sizes with `agent-browser set viewport <width> <height>`

### 8. Test Key Interactions (if applicable)

If the page has interactive elements that should work:

```bash
agent-browser click @e<ref>
agent-browser wait --load networkidle
agent-browser screenshot --annotate
```

Verify the interaction produced the expected result.

### 9. Report Findings

**If everything looks correct:**
Report that verification passed with a brief summary of what was checked.

**If issues found:**
Report each issue clearly:
- What's wrong (describe the visual/functional issue)
- Where it is (reference element refs like `@e3` and describe location)
- Screenshot evidence (the annotated screenshot shows it)
- Suggested fix if obvious

### 10. Close the Browser

```bash
agent-browser close
```
