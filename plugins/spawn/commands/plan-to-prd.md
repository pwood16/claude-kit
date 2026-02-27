---
description: Convert an implementation plan into a ralph-loop PRD JSON file with stories, priorities, and dependencies
argument-hint: "[plan-file-path] [--out output.json]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - AskUserQuestion
---

# Plan to PRD

Convert an implementation plan into a structured PRD JSON file compatible with the ralph-loop script (`/spawn:wt-agent --mode ralph --prd <file>`).

## Your Task

### 1. Locate the Plan

Parse `$ARGUMENTS` for a file path and an optional `--out <path>` flag.

- If a file path is provided, read that file as the plan
- If no file path is provided, look for a plan in the current conversation context
- If no plan is found anywhere, ask the user: "Which plan should I convert? Provide a file path or paste the plan."
- `--out <path>` sets the output file path. Default: `specs/<name>-prd.json` where `<name>` is derived from the plan title, kebab-cased (e.g., "Dashboard Analytics" becomes `specs/dashboard-analytics-prd.json`)

### 2. Analyze and Decompose

Read the plan and break it into **stories** — discrete, implementable units of work. For each story, determine:

- **`id`**: Short kebab-case identifier (e.g., `"db-schema"`, `"auth-setup"`, `"pick-api"`)
- **`title`**: One-line description of what to build
- **`description`**: 2-4 sentences explaining the work, key decisions, and where code lives
- **`acceptance_criteria`**: Array of strings — concrete, verifiable conditions for "done"
- **`priority`**: `"P0"` (must have / foundational), `"P1"` (core feature), or `"P2"` (polish / nice to have)
- **`status`**: Always `"pending"` for new PRDs
- **`blocked_by`**: Array of story `id`s that must complete before this story can start

#### Decomposition Rules

- **One story = one focused deliverable.** If a plan task touches multiple concerns (schema + API + UI), split it into separate stories.
- **Stories should be completable in a single ralph iteration.** If a story would take more than ~30 minutes of focused work, break it down further.
- **Infrastructure before features.** Config, schema, and utility stories are P0. Feature stories that depend on them are P1. Polish and edge cases are P2.
- **Explicit dependencies.** If story B reads from a table that story A creates, B must have A in its `blocked_by`. Don't leave implicit dependencies — the ralph loop respects `blocked_by` to determine work order.
- **No circular dependencies.** The dependency graph must be a DAG.
- **Group related work.** Keep stories that modify the same files close in priority so the agent builds context naturally.

### 3. Generate the PRD JSON

Derive the PRD `name` field from the plan's first heading or title, kebab-cased (e.g., "Dashboard Analytics" becomes `"dashboard-analytics"`).

Write a JSON file with this exact structure:

```json
{
  "name": "<kebab-case-name>",
  "description": "<one-line summary of what the PRD covers>",
  "stories": [
    {
      "id": "story-id",
      "title": "Short title",
      "description": "What to build and key context the agent needs.",
      "acceptance_criteria": [
        "Specific verifiable condition 1",
        "Specific verifiable condition 2"
      ],
      "priority": "P0",
      "status": "pending",
      "blocked_by": []
    }
  ]
}
```

**Important JSON rules:**
- The `stories` array is required — the ralph-loop script validates it with `jq -e '.stories'`
- Each story MUST have: `id`, `title`, `priority`, `status`, `blocked_by`
- `description` and `acceptance_criteria` are optional but strongly recommended — they give the agent clear direction
- `status` must be `"pending"` for all new stories
- `blocked_by` must reference valid story `id`s within the same PRD
- The ralph loop checks completion via: `jq '[.stories[] | select(.status != "complete" and .status != "done")] | length'`

### 4. Validate

Before writing the file, verify:
- [ ] No circular dependencies in `blocked_by`
- [ ] All `blocked_by` references point to valid story `id`s
- [ ] P0 stories have no dependencies on P1/P2 stories
- [ ] Every story has at least one acceptance criterion
- [ ] Stories are small enough for single-iteration completion

### 5. Write and Summarize

Write the JSON to the output path (creating the `specs/` directory if needed). Then show the user:

1. **File written** — path to the PRD JSON
2. **Story count** — total stories, broken down by priority (P0/P1/P2)
3. **Dependency graph** — simple ASCII showing the execution order
4. **Execution options** — use AskUserQuestion to present:
   - **Option A**: Execute with a worktree agent: `/spawn:wt-agent <name> --mode ralph --prd <output-path> --max-iterations <story-count * 2>`
   - **Option B**: "Let's work through this PRD with a team" (TeamCreate workflow for coordinated multi-agent execution)

Remind the user that everything needed for execution is captured in the PRD file — they can clear context and start a fresh session with just the PRD path.

## Example

Given a plan with "set up database, build API, create UI", the output would look like:

```json
{
  "name": "feature-x",
  "description": "Build feature X end-to-end",
  "stories": [
    {
      "id": "db-schema",
      "title": "Create database tables for feature X",
      "description": "Add feature_x and feature_x_items tables to src/db/schema.ts. Run drizzle-kit push to apply.",
      "acceptance_criteria": [
        "Tables exist in schema.ts with correct columns and constraints",
        "drizzle-kit push succeeds without errors"
      ],
      "priority": "P0",
      "status": "pending",
      "blocked_by": []
    },
    {
      "id": "api-endpoint",
      "title": "Build CRUD API for feature X",
      "description": "Server actions in src/app/(authed)/feature-x/actions.ts. Validate auth, validate input with Zod, return typed responses.",
      "acceptance_criteria": [
        "Create, read, update, delete operations work",
        "Auth is verified in every action",
        "Input validation rejects invalid data"
      ],
      "priority": "P1",
      "status": "pending",
      "blocked_by": ["db-schema"]
    },
    {
      "id": "ui-page",
      "title": "Create feature X page with form and list",
      "description": "Server component at src/app/(authed)/feature-x/page.tsx fetches data. Client component handles form submission via server actions.",
      "acceptance_criteria": [
        "Page renders list of items from database",
        "Form submits and creates new items",
        "Mobile-first responsive layout"
      ],
      "priority": "P1",
      "status": "pending",
      "blocked_by": ["api-endpoint"]
    }
  ]
}
```

**Summary output:**
```
PRD written to specs/feature-x-prd.json

Stories: 3 total
  P0: 1 (db-schema)
  P1: 2 (api-endpoint, ui-page)
  P2: 0

Dependency graph:
  db-schema
    └── api-endpoint
          └── ui-page
```
