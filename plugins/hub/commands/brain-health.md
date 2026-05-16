---
description: Health-check the ~/dev/hub/brain/ wiki against live sources and report stale topics, missing topics, and contradictions.
---

Invoke the `brain-health` skill (from the `hub` plugin).

Follow the skill's workflow exactly: discover available sources, pull recent activity, diff against the wiki, generate the report. Do not auto-update the wiki — that's `/brain`'s job. After the report, offer to run `/brain` on the stale topics.
