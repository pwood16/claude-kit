---
description: Create an Excalidraw diagram from a text description
allowed-tools: Write, Bash(mkdir:*), Read, Glob, AskUserQuestion
argument-hint: <diagram-name> <description>
---

# Create Excalidraw Diagram

Generate an Excalidraw diagram from a text description and save both `.excalidraw` and `.svg` files.

## Your Task

### 1. Parse Arguments

Arguments: `$ARGUMENTS`

Expected format: `<diagram-name> <description>`
- First word is the diagram name (used for filename)
- Remaining words are the description of what to draw

If no arguments provided, use `AskUserQuestion` to get:
- Diagram name
- What should the diagram show?

### 2. Ensure Output Directory Exists

Create the output directory if it doesn't exist:
```bash
mkdir -p docs/diagrams
```

### 3. Analyze the Description

Determine the diagram type from the description:
- **Architecture diagrams**: mentions "architecture", "system", "components", "services", "microservices", "layers"
- **Flowcharts**: mentions "flow", "process", "steps", "workflow", "sequence"
- **Entity diagrams**: mentions "entities", "relationships", "database", "schema", "ERD"
- **Network diagrams**: mentions "network", "topology", "connections", "nodes"
- **General diagrams**: anything else

### 4. Generate Valid Excalidraw JSON

Create a valid Excalidraw JSON file with these requirements:

**Required JSON structure:**
```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "claude-kit",
  "elements": [...],
  "appState": {
    "gridSize": null,
    "viewBackgroundColor": "#ffffff"
  },
  "files": {}
}
```

**Element types you can use:**
- `rectangle`: boxes for components/services
- `ellipse`: circles for nodes/states
- `diamond`: decision points
- `arrow`: connections with direction
- `line`: simple connections
- `text`: labels

**Element structure (all fields required):**
```json
{
  "id": "unique-id-1",
  "type": "rectangle",
  "x": 100,
  "y": 100,
  "width": 200,
  "height": 80,
  "angle": 0,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#a5d8ff",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "frameId": null,
  "index": "a0",
  "roundness": { "type": 3 },
  "seed": 1234567890,
  "version": 1,
  "versionNonce": 1234567890,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1234567890000,
  "link": null,
  "locked": false
}
```

**Text element additions:**
```json
{
  "type": "text",
  "text": "Label text",
  "fontSize": 20,
  "fontFamily": 1,
  "textAlign": "center",
  "verticalAlign": "middle",
  "containerId": null,
  "originalText": "Label text",
  "autoResize": true,
  "lineHeight": 1.25
}
```

**Arrow/line element additions:**
```json
{
  "type": "arrow",
  "points": [[0, 0], [200, 0]],
  "startBinding": null,
  "endBinding": null,
  "startArrowhead": null,
  "endArrowhead": "arrow",
  "elbowed": false
}
```

**Color palette (use these for consistency):**
- Blue: `#a5d8ff` (background), `#1971c2` (stroke)
- Green: `#b2f2bb` (background), `#2f9e44` (stroke)
- Yellow: `#ffec99` (background), `#f08c00` (stroke)
- Red: `#ffc9c9` (background), `#e03131` (stroke)
- Purple: `#d0bfff` (background), `#7048e8` (stroke)
- Gray: `#dee2e6` (background), `#495057` (stroke)
- Default stroke: `#1e1e1e`

**Layout guidelines:**
- Use grid-friendly coordinates (multiples of 20 or 40)
- Standard box size: 160-200 width, 60-80 height
- Spacing between elements: 80-120 pixels
- Center the diagram around coordinates (400, 300)
- Generate unique IDs using format: `element-1`, `element-2`, etc.
- Use random 10-digit numbers for `seed` and `versionNonce`
- Use current timestamp (milliseconds) for `updated`

### 5. Save the Excalidraw File

Save to: `docs/diagrams/<diagram-name>.excalidraw`

Use the `Write` tool to save the JSON.

### 6. Generate the SVG File

After saving the `.excalidraw` file, generate a corresponding SVG file at `docs/diagrams/<diagram-name>.svg`.

Convert the Excalidraw elements to SVG:
- Use the same coordinates and dimensions from the Excalidraw JSON
- Apply the same colors (strokeColor, backgroundColor)
- Convert rectangles to `<rect>` with `rx` for roundness
- Convert ellipses to `<ellipse>`
- Convert text to `<text>` elements with appropriate font styling
- Convert arrows/lines to `<path>` or `<line>` with arrow markers
- Set viewBox to encompass all elements with some padding
- Include a `<style>` block for common text styles

**SVG structure:**
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 [width] [height]" width="[width]" height="[height]">
  <style>
    /* Define text styles here */
  </style>
  <rect width="[width]" height="[height]" fill="#ffffff"/>
  <!-- Elements here -->
  <defs>
    <!-- Arrow markers here -->
  </defs>
</svg>
```

### 7. Report Results

Tell the user:
```
Created:
- docs/diagrams/<diagram-name>.excalidraw
- docs/diagrams/<diagram-name>.svg

Would you like me to add this diagram to your documentation?
```

### 8. Optional: Add to Documentation

If user agrees, use `Glob` and `Read` to find relevant markdown files (README.md, docs/*.md) and offer to add an image reference:
```markdown
![<diagram-name>](docs/diagrams/<diagram-name>.svg)
```

## Example Diagrams

### Architecture Example
For "API gateway with microservices":
- Rectangle for API Gateway (top center)
- Rectangles for each microservice (row below)
- Rectangle for database (bottom)
- Arrows connecting them

### Flowchart Example
For "User login flow":
- Ellipse for Start
- Rectangles for steps
- Diamond for decisions
- Ellipse for End
- Arrows with labels

## Notes

- Always generate valid JSON that Excalidraw can open
- Include enough elements to meaningfully represent the description
- Use appropriate colors to distinguish different types of components
- Ensure arrows connect logical relationships
- Add text labels to clarify what each element represents
