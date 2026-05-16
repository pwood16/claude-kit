---
name: iterate-diagram
description: Visually iterate on an HTML file using Playwright screenshots. Use when working on HTML diagrams, HTML review pages produced by review-doc, dashboards, or any HTML where you need to see how it looks and tighten layout, styling, and content.
argument-hint: "<html-file-path>"
---

# Iterate Diagram

You are visually iterating on an HTML file. Your workflow is:

## Screenshot → Review → Edit → Repeat

### 1. Take a screenshot

Use the screenshot script to capture the current state. The script requires Playwright. Prefer per-project install: `npx playwright install chromium` (run once; the script auto-resolves Playwright via `npx`/local `node_modules`). A global install (`npm install -g playwright`) also works if you prefer system-wide.

```bash
node ${SKILL_DIR}/scripts/screenshot.js <html-file> <output.png> [options]
```

`${SKILL_DIR}` is the directory containing this `SKILL.md` (i.e., `…/plugins/review/skills/iterate-diagram/`). Resolve it from the path you read this file from.

**Options:**

- `--width=N` — viewport width (default: 2560)
- `--height=N` — viewport height (default: 1440)
- `--zoom=N` — set zoom level (assumes `state.zoom` / `applyTransform()` globals)
- `--pan=X,Y` — set pan offset
- `--click="Button Text"` — click a text element before screenshot
- `--eval="js code"` — execute JavaScript in the page (can use multiple times)
- `--full` — capture full page scroll height

**Common patterns:**

```bash
# Basic screenshot
node ${SKILL_DIR}/scripts/screenshot.js diagram.html shot.png

# Toggle a mode and zoom out
node ${SKILL_DIR}/scripts/screenshot.js diagram.html shot.png --click="Toggle Mode" --zoom=0.5

# Run arbitrary JS to set state
node ${SKILL_DIR}/scripts/screenshot.js diagram.html shot.png --eval="state.showAllLines=true; render();"

# Multiple actions chained
node ${SKILL_DIR}/scripts/screenshot.js diagram.html shot.png \
  --click="Show All Groups" \
  --eval="state.zoom=0.45; applyTransform();"
```

The script prints the absolute path of the saved screenshot.

### 2. Show the screenshot

Read the screenshot file with the Read tool to display it to the user. Always show the screenshot — never describe what you think it looks like without showing it.

### 3. Get feedback or assess yourself

If the user provided specific instructions, apply them. Otherwise, critically review the screenshot using the checklist below. The goal is a diagram or page that someone unfamiliar with the system can scan and understand the key relationships within 30 seconds.

#### Readability & Clarity

- **Can you read every card title and field name?** If text is too small at the current zoom, either zoom in for detail shots or increase font sizes.
- **Is there a clear visual hierarchy?** The eye should be drawn to the most important entities first before peripheral ones.
- **Are group/zone labels visible and distinct?** Zone labels should be readable but not compete with entity cards.
- **Do badges and annotations (NEW, LEGACY, "Replaces X") stand out?** They should be immediately noticeable, not buried.

#### Layout & Spacing

- **Are cards overlapping or clipping into zone borders?** Every card should have breathing room — at least 20-30px from zone edges and neighboring cards.
- **Are zone backgrounds overlapping each other?** Zones should not bleed into adjacent zones.
- **Is there consistent spacing?** Cards within a group should be evenly spaced. Groups at the same level should align horizontally or vertically.
- **Is the layout scannable top-to-bottom or left-to-right?** Hierarchies should flow in a consistent direction. Parent entities above children, or left-to-right for peer relationships.

#### Relationship Lines

- **Are lines crossing through unrelated cards?** This is the #1 readability killer. If a line from A to B passes through card C, reposition cards to eliminate the crossing.
- **Are there clusters of overlapping lines?** Fan-out from a central entity should be spread so individual lines are distinguishable.
- **Can you trace each line from source to target?** If lines merge into an unreadable tangle, consider: repositioning entities closer together, reducing visible relationships (use tier/secondary filtering), or adding curve offsets.
- **Are line labels readable?** Cardinality labels (1:N, M:N) should not overlap each other or sit on top of cards.
- **Do dashed vs solid lines clearly convey optional vs required?** The visual distinction should be obvious.

#### Color & Contrast

- **Do group colors help or hinder?** Each group should have a distinct hue. If two adjacent zones look too similar, adjust colors.
- **Is the background working?** Card text, line labels, and zone labels should all be legible against the canvas.
- **Do NEW/LEGACY/deprecated states have enough contrast?** These should be immediately scannable without squinting.

#### Multi-State Testing

- **Test every toggle/mode** the diagram supports. A diagram that looks great in one state but breaks in another is not done.
- **Check at multiple zoom levels.** The diagram should be usable at both zoomed-out overview (0.4-0.6) and zoomed-in detail (0.8-1.0).
- **Check with different group combinations toggled on.** Subsets of groups should render cleanly, not just "show all."

### 4. Edit the HTML

Make targeted edits to the HTML file. Prefer small position/style tweaks over large rewrites. Common fixes:

**Positioning (most common):**

- Adjust `position: { x, y }` values to move entity cards
- Modify `zone: { x, y, w, h }` to resize/reposition group backgrounds
- Shift entire groups by applying an offset to all entities in that group

**Eliminating line crossings:**

- Move the source or target card so the line has a clear path
- If two entities are connected but far apart with entities in between, move them closer or to the same row/column
- Reorder entities within a zone to minimize crossovers

**Improving hierarchy:**

- Place parent entities above children (lower y = higher on screen)
- Center heavily-connected entities and arrange satellites around them
- Keep related entities in adjacent positions — FK targets should be near FK sources

**Spacing fixes:**

- Use consistent x/y increments between cards (e.g., 260px horizontal, 170px vertical for standard cards)
- Ensure zone dimensions fully contain their entities with padding

**Style tweaks:**

- CSS changes for font sizes, colors, border widths
- Card min/max widths for better text fitting
- Line stroke-width or opacity for emphasis/de-emphasis

### 5. Re-screenshot and iterate

After each edit, take a new screenshot and show it. Explicitly call out what improved and what still needs work. Continue until:

- No cards overlap
- No lines cross through unrelated cards
- All text is readable
- The layout tells a clear story
- The user confirms it looks good

## Pairs naturally with

- `review-doc` — generates HTML review pages from markdown. Use `iterate-diagram` on the produced `*-review.html` to tighten layout/contrast before sharing.

## When NOT to use

| Don't | Do instead |
|---|---|
| The HTML is broken / won't render | Fix the JS/markup error first; iterate-diagram screenshots the rendered output, not the source |
| You only need one quick screenshot, no iteration | Run the script directly; the skill's value is the review-and-edit loop |
| The file is plain text or markdown | This is for rendered HTML only — for markdown content, edit the source directly |

## Important notes

- The HTML file path is: `$ARGUMENTS`
- Save screenshots in the same directory as the HTML file (or a `screenshots/` subdirectory if it exists)
- Always use absolute paths for the HTML file
- When the file has interactive state (toggles, modes), test multiple states
- Name screenshots descriptively (e.g., `current-state.png`, `evolution-mode.png`)
