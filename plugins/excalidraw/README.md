# Excalidraw Plugin

Create Excalidraw diagrams from text descriptions and export to SVG.

![How the Excalidraw plugin works](../../docs/diagrams/plugin-workflow.svg)

## Commands

### `/excalidraw:create <diagram-name> <description>`

Generate a diagram from a text description.

**Usage:**

```bash
/excalidraw:create architecture-diagram Create a system architecture showing the API gateway, microservices, and database layer

/excalidraw:create login-flow User authentication flow with email verification

/excalidraw:create network-topology Network diagram showing load balancer, web servers, and database cluster
```

**What it does:**

1. Parses your description to determine diagram type
2. Generates valid Excalidraw JSON with appropriate shapes and connections
3. Saves to `docs/diagrams/<name>.excalidraw`
4. Generates SVG export at `docs/diagrams/<name>.svg`
5. Offers to add diagram to your documentation

**Output:**

```
Created:
- docs/diagrams/architecture-diagram.excalidraw
- docs/diagrams/architecture-diagram.svg

Would you like me to add this diagram to your documentation?
```

## Supported Diagram Types

The command automatically detects diagram type from your description:

- **Architecture diagrams**: system components, services, layers
- **Flowcharts**: processes, workflows, decision trees
- **Entity diagrams**: database schemas, relationships
- **Network diagrams**: topology, connections, nodes
- **General diagrams**: any visual representation

## Editing Diagrams Manually

To make manual edits to a generated diagram:

1. Open [excalidraw.com](https://excalidraw.com) in your browser
2. Click the **menu icon** (☰) in the top-left corner
3. Select **Open** and choose your `.excalidraw` file
4. Make your edits using the Excalidraw editor

**Saving your changes:**

After editing, you need to update both files:

1. **Save the `.excalidraw` file**: Menu (☰) → Export to file → Save to disk
2. **Export the `.svg` file**: Menu (☰) → Export image → Select "SVG" → Export

Make sure to save both files to `docs/diagrams/` with the same base name to keep them in sync.

**VS Code alternative:**

The [Excalidraw VS Code extension](https://marketplace.visualstudio.com/items?itemName=pomdtr.excalidraw-editor) lets you edit `.excalidraw` files directly in your editor. To export SVG from VS Code, use the command palette: `Excalidraw: Export to SVG`.

## Installation

### From claude-kit marketplace

```bash
# Add the marketplace
claude plugin marketplace add pwood16/claude-kit

# Install the plugin
claude plugin install excalidraw@claude-kit --scope user
```

### Local development

```bash
claude --plugin-dir /path/to/claude-kit/plugins/excalidraw
```

## Permissions

**What this command can do:**

- Create directories (`mkdir`)
- Write `.excalidraw` and `.svg` files
- Read existing docs for integration

**What it cannot do:**

- Execute arbitrary commands
- Modify files outside the project
