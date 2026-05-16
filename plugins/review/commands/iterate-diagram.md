---
description: Visually iterate on an HTML file (diagram, dashboard, review page) using Playwright screenshots — screenshot, review, edit, repeat.
argument-hint: "<html-file-path>"
---

Invoke the `iterate-diagram` skill (from the `review` plugin) with arguments: `$ARGUMENTS`.

If `$ARGUMENTS` is empty, ask for the HTML file path. Otherwise treat `$ARGUMENTS` as the absolute path to the HTML file.

Follow the skill's workflow exactly: screenshot → show → review/feedback → edit → re-screenshot. Use the Playwright script at `${SKILL_DIR}/scripts/screenshot.js` (resolve the skill dir from where you read the SKILL.md).
