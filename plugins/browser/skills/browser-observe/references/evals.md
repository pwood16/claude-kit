# browser-observe evals

Use these to verify the skill activates correctly and produces the expected report shape. Re-run on every model upgrade or skill edit.

## Should activate

1. *"I keep getting redirected to /sign-in even though I'm logged in. What's happening?"*
2. *"The dashboard shows a blank page after I click 'Save'."*
3. *"Why does navigating to /settings flash the homepage first?"*
4. *"The page just hangs — never finishes loading."*
5. *(After 5+ minutes of source reading)* "I can't figure out why this navigation isn't sticking."

For each, the skill should fire and the report should include the request sequence, errors, final URL, and at least one red-flag check.

## Should NOT activate

1. *"This TypeScript error says `Property 'foo' does not exist on type 'Bar'`."* — Static code error; read the file.
2. *"`npm run build` fails with `Module not found: ./missing`."* — Build error, no runtime.
3. *"The /api/users endpoint returns 500. Here's the server log: …"* — Backend bug with provided evidence.
4. *"Here's the network HAR I captured. What's wrong?"* — User already provided observation data.
5. *"Add error handling to the fetchUser function."* — Code task, no debugging.

## Sample expected report

```
## Observation Report: http://localhost:3000/dashboard

### Request Sequence
1. GET /dashboard → 200
2. GET /api/me → 401
3. Navigation to /sign-in
4. GET /sign-in → 200
5. GET /api/me → 401
6. Navigation to /sign-in (LOOP)

### Errors
- Console: "Unauthorized" thrown from src/lib/api-client.ts:42
- Page errors: (none)

### Final URL
http://localhost:3000/sign-in (still navigating; sampled twice, both /sign-in)

### Red Flags
- [x] 4xx/5xx responses: GET /api/me → 401 (twice)
- [x] Redirect chain: /dashboard → /sign-in → /sign-in (loop)
- [x] Suspicious request: /api/me called on /sign-in page
- [ ] Repeated identical requests (covered by loop above)

### Hypothesis
The sign-in page is calling /api/me (probably from a global provider or root
layout), getting 401, and the auth guard redirects to /sign-in — which then
re-runs the same call. Look at the root layout and any auth provider
mounted globally; the call should be skipped on /sign-in.
```

## Failure modes to watch for in eval review

- Skill fires on a static type error or build failure (over-trigger — tighten description)
- Skill stays quiet on a "blank page" or "redirect loop" report (under-trigger — broaden trigger language)
- Report omits any of: request sequence, errors, final URL (workflow not followed end-to-end)
- Hypothesis offered before observation (anti-rationalization not landing)
- Re-observation when user already provided HAR/network output (When-NOT-to-use ignored)
