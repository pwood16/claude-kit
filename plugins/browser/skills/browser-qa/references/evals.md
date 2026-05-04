# browser-qa evals

Use these to verify the skill activates correctly and produces the expected report shape. Re-run on every model upgrade or skill edit.

## Should activate

These prompts represent the user intent the skill is designed for.

1. *"I just added a confirmation modal to the checkout page — can you check it looks right?"*
2. *"The login form looks broken on mobile, can you take a look?"*
3. *(After Claude edits `src/components/Header.tsx`)* "Verify the header rendered correctly."
4. *"Make sure the new pricing table doesn't overflow on small screens."*
5. *"I refactored the navigation. Does it still work?"*

For each, the skill should fire and the report should include: at least one annotated screenshot, an interactive snapshot, and a verdict.

## Should NOT activate

These look adjacent but the skill should stay quiet.

1. *"Why is `useFoo` returning null?"* — debugging a hook, not visual rendering. (`browser-observe` may apply if symptom is runtime.)
2. *"Update the README to mention the new component."* — docs change, no rendered output.
3. *"Refactor `formatPrice` to accept a currency arg."* — pure utility refactor, no UI impact.
4. *"Bump the React version in package.json."* — config change, no immediate UI verification needed.
5. *"The /api/users endpoint is returning 500."* — backend failure, no browser QA needed.

## Sample expected report

```
## QA Report: http://localhost:3000/checkout

### Verified
- Page loads to networkidle: pass
- Modal renders on "Confirm" click: pass
- Modal close button (@e7) returns to checkout: pass
- Mobile viewport (375x812): pass — layout adapts, no overflow

### Issues
- Modal heading uses default font weight; design spec calls for 600 (visible in screenshot, header element @e4)

### Console / errors
- (none)

### Verdict
- 1 visual issue, otherwise pass
```

## Failure modes to watch for in eval review

- Skill fires on a backend-only change (over-trigger — tighten description)
- Skill stays quiet on a clear visual change request (under-trigger — broaden trigger language)
- Report omits the screenshot or console check (workflow not being followed end-to-end)
- "Pass" reported when console showed errors (verification not gated on evidence)
