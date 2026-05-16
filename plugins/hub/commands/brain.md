---
description: Compile the second-brain wiki at ~/dev/hub/brain/ from hub sources. Pass an optional domain to recompile just that topic.
argument-hint: "[domain-name]"
---

Invoke the `brain` skill (from the `hub` plugin) with arguments: `$ARGUMENTS`.

If `$ARGUMENTS` is empty, run a full compile. Otherwise treat `$ARGUMENTS` as the target domain name and run a targeted compile.

Follow the skill's workflow exactly. Report changes when done — new topics, updated topics, source counts.
