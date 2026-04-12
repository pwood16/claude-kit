---
description: Extract and summarize content from a web page using agent-browser
allowed-tools:
  - Bash(agent-browser:*)
  - Bash(which agent-browser:*)
  - Read
argument-hint: <url>
---

# Browser Read Command

Extract content from web pages that are difficult to scrape — SPAs, Twitter/X, auth-gated content, JavaScript-heavy sites.

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

### 3. Open the Page

```bash
agent-browser open "$URL"
```

### 4. Wait for Full Load

```bash
agent-browser wait --load networkidle
```

Some pages (especially SPAs like Twitter/X) need extra time for dynamic content to render. If the first snapshot looks incomplete, wait and re-snapshot:

```bash
agent-browser wait 2000
```

### 5. Screenshot for Visual Context

```bash
agent-browser screenshot
```

Review the screenshot to understand the page layout and identify the main content area.

### 6. Snapshot the Page

```bash
agent-browser snapshot
```

This returns a compact accessibility tree with element refs (`@e1`, `@e2`, etc.).

### 7. Extract Content

Based on the snapshot, extract text from the main content elements:

```bash
agent-browser get text @e<ref>
```

**For different page types:**

**Twitter/X threads:**
- Identify tweet elements in the snapshot
- Extract text from each tweet in the thread
- Scroll down to load more replies if needed: `agent-browser scroll down 500` then `agent-browser snapshot`
- Repeat scroll + snapshot until you've captured the full thread
- Note: X lazy-loads content — you may need 2-3 scroll cycles

**Articles / blog posts:**
- Find the article body element and extract its text
- Preserve headings and structure
- Skip navigation, sidebars, ads

**Documentation:**
- Preserve heading hierarchy
- Capture code blocks
- Maintain list structure

**General pages:**
- Focus on the main content area
- Skip repeated nav/footer/sidebar content

### 8. Handle Long Pages

For pages that extend beyond the viewport:

```bash
agent-browser scroll down 500
agent-browser snapshot
```

Repeat until you've captured all content. Use `agent-browser get text @ref` on new elements that appear.

To avoid token bloat on very large pages, use `--max-output 5000` on snapshot commands:

```bash
agent-browser snapshot --max-output 5000
```

### 9. Close the Browser

```bash
agent-browser close
```

### 10. Present the Content

Summarize the extracted content in a clean, organized format:

- **Thread/conversation:** Present each post in order with author attribution
- **Article:** Title, author, date, then body text with structure preserved
- **Documentation:** Preserve heading hierarchy and code blocks
- **General:** Organize by the page's own structure

If the user asked a specific question about the page, answer it directly using the extracted content rather than dumping raw text.
