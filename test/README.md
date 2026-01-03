# Test Fixtures

## Capturing SessionEnd Data

To capture real SessionEnd hook data for testing:

1. **Add the echo hook to your settings**:

Edit `~/.claude/settings.json` and add:

```json
{
  "hooks": {
    "SessionEnd": [{
      "hooks": [{
        "type": "command",
        "command": "~/.claude/prior-sessions-test/echo-hook.sh"
      }]
    }]
  }
}
```

2. **Generate test data** by running `/clear` in different scenarios:
   - Normal session with work done
   - Long session with many messages
   - Session with no git repo
   - Different projects/branches

3. **Captured data** is saved to:
   - `~/.claude/prior-sessions-test/captured-*.json`

4. **Copy useful fixtures** to `test/fixtures/`:
   ```bash
   cp ~/.claude/prior-sessions-test/captured-20260102_183045.json \
      test/fixtures/sessionend-clear-normal.json
   ```

5. **Remove the echo hook** from settings.json when done collecting data.

## Using Fixtures for Development

Once you have fixtures, you can test the hook script without running `/clear`:

```bash
# Test hook script with fixture
cat test/fixtures/sessionend-clear-normal.json | ./hooks-handlers/on-clear.sh
```

## Fixture Naming Convention

- `sessionend-clear-*.json` - SessionEnd with reason: "clear"
- `sessionend-logout-*.json` - SessionEnd with reason: "logout"
- `sessionend-exit-*.json` - SessionEnd with reason: "other"
- Descriptive suffixes: `-normal`, `-long-session`, `-no-git`, etc.
