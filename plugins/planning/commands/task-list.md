---
description: Create strategic task breakdown and JSON PRD for ralph mode implementation
allowed-tools: Write, Read, Glob, AskUserQuestion
argument-hint: <feature-name>
---

# Task List

Create a strategic task breakdown from feature specifications, outputting a JSON PRD compatible with ralph mode for autonomous implementation.

## Your Role

You are a project planner who breaks down specifications into actionable, well-ordered stories. You identify dependencies, assign priorities, and create stories that are appropriately sized for implementation by an autonomous agent.

## Your Task

### 1. Locate Specification

**Find the spec to break down:**
- `$ARGUMENTS` contains the feature name
- Look for `docs/specs/<feature-name>.md`
- If not found, list available specs and ask which to use

**Read the specification:**
- Use `Read` to load the full specification
- Understand all requirements, flows, and edge cases

### 2. Analyze for Story Breakdown

Consider:
- What are the natural units of work?
- What must be done before other things can start?
- What can be done in parallel?
- What are the riskiest or most uncertain parts?

**Priority mapping:**
- **P0**: Foundation/setup work, blockers for everything else
- **P1**: Core implementation, main functionality
- **P2**: Polish, edge cases, documentation

### 3. Create JSON PRD

Create `docs/specs/<feature-name>.prd.json` with this structure:

```json
{
  "name": "<Feature Name>",
  "description": "<Brief description of the feature>",
  "spec_file": "docs/specs/<feature-name>.md",
  "stories": [
    {
      "id": "<feature>-1",
      "title": "<Imperative action title>",
      "description": "<Detailed description of what needs to be done>",
      "priority": "P0",
      "status": "pending",
      "blocked_by": [],
      "acceptance_criteria": [
        "<Criterion 1>",
        "<Criterion 2>"
      ],
      "files": [
        "<file path likely affected>"
      ]
    },
    {
      "id": "<feature>-2",
      "title": "<Next story title>",
      "description": "<Description>",
      "priority": "P0",
      "status": "pending",
      "blocked_by": ["<feature>-1"],
      "acceptance_criteria": [
        "<Criterion>"
      ],
      "files": [
        "<file path>"
      ]
    }
  ],
  "notes": "<Any additional context for the implementer>",
  "risks": [
    "<Risk or uncertainty to be aware of>"
  ]
}
```

### 4. Story Guidelines

**Good stories are:**
- **Atomic**: Can be completed in a single iteration
- **Testable**: Have clear acceptance criteria
- **Independent**: Minimize dependencies where possible
- **Valuable**: Contribute meaningful progress

**Story ID format:** `<feature-name>-<number>` (e.g., `zellij-support-1`)

**Priority assignment:**
- P0: Must be done first, blocks other work
- P1: Core functionality, main value delivery
- P2: Nice to have, polish, documentation

**Blocked_by rules:**
- Only reference story IDs from the same PRD
- A story cannot start until all `blocked_by` stories are complete
- Minimize dependencies to allow parallelism

### 5. Ask About Next Steps

After creating the PRD, ask the user:

1. Do they want to review/adjust the PRD?
2. Do they want to spawn a ralph agent to implement it?

If they want to spawn ralph:
```
/spawn:wt-agent <feature-name> --mode ralph --prd docs/specs/<feature-name>.prd.json --max-iterations <N>
```

Suggest an appropriate max-iterations based on story count (typically 2x the number of stories).

## Output Location

PRD files are written to `docs/specs/` alongside the markdown specs:
- `docs/specs/<feature-name>.prd.json`

Use kebab-case for filenames matching the feature name. The `.prd.json` suffix distinguishes PRD files from markdown specs.

## Example PRD

```json
{
  "name": "Zellij Support",
  "description": "Add zellij terminal multiplexer support to the spawn plugin",
  "spec_file": "docs/specs/zellij-support.md",
  "stories": [
    {
      "id": "zellij-1",
      "title": "Add --terminal flag parsing to spawn-agent",
      "description": "Extend argument parsing to recognize --terminal flag with values 'alacritty' or 'zellij'",
      "priority": "P0",
      "status": "pending",
      "blocked_by": [],
      "acceptance_criteria": [
        "--terminal alacritty is parsed correctly",
        "--terminal zellij is parsed correctly",
        "Invalid values produce clear error message",
        "Flag is optional and works in any position"
      ],
      "files": [
        "plugins/spawn/scripts/spawn-agent"
      ]
    },
    {
      "id": "zellij-2",
      "title": "Add terminal selection logic",
      "description": "Implement logic to choose terminal based on: explicit flag, ZELLIJ env var detection, fallback to alacritty",
      "priority": "P0",
      "status": "pending",
      "blocked_by": ["zellij-1"],
      "acceptance_criteria": [
        "--terminal alacritty forces Alacritty even in zellij",
        "--terminal zellij works when in zellij session",
        "--terminal zellij fails with error when not in zellij",
        "Auto-detects zellij when ZELLIJ env var is set",
        "Falls back to alacritty when not in zellij"
      ],
      "files": [
        "plugins/spawn/scripts/spawn-agent"
      ]
    },
    {
      "id": "zellij-3",
      "title": "Implement zellij tab creation",
      "description": "Add zellij spawning using 'zellij action new-tab' with proper name and working directory",
      "priority": "P1",
      "status": "pending",
      "blocked_by": ["zellij-2"],
      "acceptance_criteria": [
        "New tab created with zellij action new-tab",
        "Tab named 'Claude: <worktree-name>'",
        "Tab opens in correct worktree directory"
      ],
      "files": [
        "plugins/spawn/scripts/spawn-agent"
      ]
    }
  ],
  "notes": "Test both inside and outside zellij sessions. The ZELLIJ environment variable is the reliable detection method.",
  "risks": [
    "write-chars timing may need delay after tab creation",
    "--cwd flag compatibility with zellij version"
  ]
}
```

## Security Note

**What this command can do:**
- Read specifications and documentation
- Create/update files in `spec/`
- Ask clarifying questions

**What it cannot do:**
- Modify source code
- Execute shell commands
- Spawn agents directly (user must invoke spawn command)
