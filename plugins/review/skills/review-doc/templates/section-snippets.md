# Section snippets

HTML fragments to compose the `{{BODY}}` of `base.html`. Pick the ones that match the source markdown. Order: context → diagram (optional) → reviewable cards → questions (optional) → updates table (optional) → general notes (required, last).

---

## 1. Recap / context section (NOT reviewable — no status, no comment)

Use for preamble, design recap, problem framing. Brief — don't restate the whole doc. Include the anchor list here so it's near the top.

```html
<div class="section">
  <h2>Design recap</h2>
  <p class="recap-text">
    One or two short paragraphs. Use <code>inline code</code> for identifiers. Cite the source markdown — don't expand it.
  </p>
  <ul class="anchor-list">
    <li><a href="#section-a">A · short label</a></li>
    <li><a href="#section-b">B · short label</a></li>
    <li><a href="#questions">Open questions</a></li>
  </ul>
</div>
```

---

## 2. Diagram section (NOT reviewable)

Only if the source has sequencing / lifecycle / dependency information. Hand-roll the SVG — no CDN libs. Use a 980×N viewBox, lane labels on the left, color-coded boxes matching the lane palette below.

```html
<div class="section">
  <h2>Sequencing</h2>
  <div class="diagram-wrap">
    <svg viewBox="0 0 980 220" xmlns="http://www.w3.org/2000/svg" style="width:100%; max-width:980px; height:auto;">
      <!-- lane labels -->
      <text x="20" y="40" font-size="11" font-weight="700" fill="#6C7C77" letter-spacing="0.8">FOUNDATION</text>
      <text x="20" y="120" font-size="11" font-weight="700" fill="#6C7C77" letter-spacing="0.8">UI</text>

      <!-- lane separators -->
      <line x1="120" y1="55" x2="980" y2="55" stroke="#EDF1EE" stroke-width="1"/>

      <!-- box -->
      <rect x="130" y="14" width="150" height="36" rx="6" fill="#ECEDFB" stroke="#4F55C0" stroke-width="1.5"/>
      <text x="205" y="36" font-size="12" font-weight="700" fill="#4F55C0" text-anchor="middle">A · label</text>

      <!-- arrow -->
      <line x1="282" y1="32" x2="318" y2="32" stroke="#6C7C77" stroke-width="1.5"/>
      <polygon points="318,32 312,29 312,35" fill="#6C7C77"/>
    </svg>
    <div class="diagram-caption">Critical path note here.</div>
  </div>
</div>
```

Palette:
- Foundation: fill `#ECEDFB` stroke `#4F55C0` text `#4F55C0`
- Composition: fill `#F3E8FB` stroke `#6B3FB0` text `#6B3FB0`
- UI: fill `#FFF6E5` stroke `#C2843F` text `#8C5A1F`
- Stretch: fill `#FBEAEA` stroke `#B03F3F` text `#B03F3F`
- Pending (dashed): same as UI but `stroke-dasharray="4,3"`

---

## 3. Reviewable card (status pills + comment)

The main pattern. One per reviewable section in the source.

```html
<div class="ticket lane-foundation" id="section-a">
  <div class="ticket-head">
    <div class="ticket-title-block">
      <div class="ticket-id">SECTION A · LANE LABEL</div>
      <div class="ticket-title">Short title from the source</div>
      <div class="ticket-meta">
        <span class="badge badge-blue">repo / area</span>
        <span class="badge badge-gray badge-size">S · ~2-3 hr</span>
        <span class="badge badge-blue">Owner: name</span>
      </div>
    </div>
  </div>
  <div class="ticket-body">
    <p>One or two paragraphs from the source.</p>
    <pre><code>code block if relevant</code></pre>
    <div class="acceptance">
      <h4>Acceptance</h4>
      <ul>
        <li>Item one</li>
        <li>Item two</li>
      </ul>
    </div>
  </div>
  <div class="review-block" data-ticket="A" data-reviewable="true"></div>
</div>
```

Lane classes: `lane-foundation` (blue), `lane-composition` (purple), `lane-ui` (amber), `lane-stretch` (red), `lane-pending` (dashed amber), `lane-neutral` (gray default).

Badge classes match lane: `badge-blue`, `badge-purple`, `badge-amber`, `badge-red`, `badge-gray`, `badge-green`.

---

## 4. Question card (comment-only — no status pills)

For open questions / things to confirm. Pin the target audience.

```html
<div class="question">
  <div class="question-target">Product / name</div>
  <div class="question-q">The question itself, as a sentence.</div>
  <p style="font-size: 13px; color: var(--text-secondary); margin: 4px 0 8px;">Optional context for the question.</p>
  <div class="review-block" data-ticket="q1"></div>
</div>
```

For engineering questions add `class="question target-eng"` and `<div class="question-target eng">Eng / name</div>`.

Wrap a group of questions in a section:

```html
<div class="section" id="questions">
  <h2>Open questions</h2>
  <h3>For product</h3>
  <!-- question cards -->
  <h3>For engineering</h3>
  <!-- question cards -->
</div>
```

---

## 5. Updates table (comment-only)

For "existing things to update" lists.

```html
<div class="section" id="updates" style="margin-top: 32px;">
  <h2>Existing items to update</h2>
  <table class="update-table">
    <thead><tr><th>Item</th><th>Action</th></tr></thead>
    <tbody>
      <tr><td><strong>TICKET-XXX</strong></td><td>What to change.</td></tr>
    </tbody>
  </table>
  <div class="review-block" data-ticket="updates" style="margin-top: 18px;"></div>
</div>
```

---

## 6. General notes (REQUIRED — always last)

Single textarea at the bottom. The script wires it up via `data-ticket="general"`.

```html
<div class="section">
  <h2>General notes</h2>
  <p style="font-size: 13px; color: var(--text-muted); margin: 4px 0 10px;">Anything that doesn't fit a specific section.</p>
  <textarea class="comment" data-ticket="general" placeholder="Overall thoughts, missing pieces, things to discuss…" style="min-height: 100px;"></textarea>
</div>
```

---

## Group labels

Between groups of cards (e.g., between context and the reviewable cards):

```html
<h2 class="group-label">New sections (7)</h2>
```
