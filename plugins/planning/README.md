# Planning Plugin

Product planning and specification agents for structured development workflows.

## Overview

The planning plugin provides a suite of specialized agents that guide you through the full product development lifecycle - from vision to implementation. Each agent focuses on a specific phase, creating documentation that flows naturally into the next step.

## Commands

### `/planning:product-planner`

Creates product vision, mission, and roadmap through guided discovery.

**Output:** `docs/product/vision.md`, `docs/product/roadmap.md`

```
/planning:product-planner my-app
```

The product planner asks discovery questions about:
- Problem being solved and target users
- Vision and mission
- Core principles and values
- Strategic roadmap phases

### `/planning:spec-shaper`

Gathers and clarifies requirements through targeted questions.

**Output:** Conversation-based (no files created)

```
/planning:spec-shaper user-authentication
```

The spec shaper explores:
- Functional requirements
- Edge cases and error handling
- Constraints and dependencies
- User experience details
- Scope boundaries

This is a read-only exploration phase that shapes requirements before formal documentation.

### `/planning:spec-writer`

Creates detailed specification documentation for a feature.

**Output:** `docs/specs/<feature-name>.md`

```
/planning:spec-writer user-authentication
```

The spec writer produces formal documentation including:
- Functional and non-functional requirements
- User flows
- Data models and API contracts
- Edge cases and error handling
- Technical implementation notes

### `/planning:task-list`

Creates a JSON PRD from specifications, compatible with ralph mode for autonomous implementation.

**Output:** `docs/specs/<feature-name>.prd.json`

```
/planning:task-list user-authentication
```

The task list creates a structured PRD with:
- Stories with priorities (P0, P1, P2)
- Dependencies between stories (`blocked_by`)
- Acceptance criteria for each story
- Files likely to be affected

The PRD can be used directly with ralph mode:
```
/spawn:wt-agent user-auth --mode ralph --prd docs/specs/user-authentication.prd.json --max-iterations 20
```

### `/planning:implementer`

Implements features following specifications and task lists.

**Output:** Code changes per specification

```
/planning:implementer user-authentication
```

The implementer:
- Follows specifications precisely
- Works through tasks in order
- Updates task status as work completes
- Maintains code quality standards

## Workflow Example

A typical workflow progresses through each phase:

```
# 1. Define product direction
/planning:product-planner my-saas-app

# 2. Shape requirements for a feature (conversational)
/planning:spec-shaper user-authentication

# 3. Write formal specification
/planning:spec-writer user-authentication

# 4. Create JSON PRD for implementation
/planning:task-list user-authentication

# 5a. Implement manually with guidance
/planning:implementer user-authentication

# 5b. OR spawn autonomous ralph agent
/spawn:wt-agent user-auth --mode ralph --prd docs/specs/user-authentication.prd.json --max-iterations 20
```

You don't have to use every step - jump in where appropriate:
- Have a clear vision already? Start with spec-shaper
- Requirements are clear? Go straight to spec-writer
- Have a spec? Create PRD and spawn ralph to implement

## Output Structure

All planning artifacts are organized under `docs/`:

```
docs/
├── product/
│   ├── vision.md              # Product vision, mission, principles
│   └── roadmap.md             # Strategic roadmap and phases
└── specs/
    ├── feature-a.md           # Detailed specification (markdown)
    ├── feature-a.prd.json     # JSON PRD for ralph mode
    ├── feature-b.md
    └── feature-b.prd.json
```

The `.prd.json` files can be used directly with ralph mode for autonomous implementation.

## Integration with Ralph Mode

The `task-list` command outputs a JSON PRD that works directly with the spawn plugin's ralph mode:

```bash
# Create PRD from spec
/planning:task-list my-feature

# Spawn autonomous agent to implement
/spawn:wt-agent my-feature --mode ralph --prd docs/specs/my-feature.prd.json --max-iterations 20
```

Ralph mode will:
- Work through stories in priority order (P0 → P1 → P2)
- Respect `blocked_by` dependencies
- Verify `acceptance_criteria` before marking stories complete
- Commit after each iteration
- Track progress in `<prd-name>-progress.txt`

## Installation

Add to your Claude settings:

```json
{
  "plugins": ["claude-kit/plugins/planning"]
}
```

Or use with plugin directory:

```bash
claude --plugin-dir ./plugins/planning
```
