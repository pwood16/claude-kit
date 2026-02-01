# Feature: Goodbye World Function

## Feature Description
Add a simple, reusable "goodbye" function that prints 'Goodbye World' to complement the existing hello function and demonstrate basic function implementation. This function will be implemented as a standalone Python script in the scripts directory, following the same pattern as the hello.py script.

## User Story
As a developer
I want a simple goodbye function that prints 'Goodbye World'
So that I can have another basic utility function for testing, examples, and demonstrations

## Problem Statement
The claude-kit project has a hello function that prints 'Hello World', but lacks a complementary goodbye function. Having both greeting and farewell utilities provides a more complete set of example functions and demonstrates consistency in implementation patterns.

## Solution Statement
Create a simple Python script with a `goodbye()` function that prints 'Goodbye World' to stdout. The script will:
1. Define a clean, callable `goodbye()` function
2. Be executable from the command line
3. Follow the exact same pattern as the existing hello.py script (uv-compatible, properly structured)
4. Include a simple CLI interface for standalone execution
5. Mirror the hello.py implementation for consistency

## Relevant Files
Use these files to implement the feature:

- `scripts/hello.py` - Existing hello function that serves as the template/pattern to follow for the goodbye function. This file demonstrates the exact structure, documentation style, and CLI interface pattern to replicate.

### New Files
- `scripts/goodbye.py` - The goodbye world function implementation as a standalone Python script, following the same structure as hello.py

## Implementation Plan
### Phase 1: Foundation
Create the basic script structure with proper shebang and imports, following the exact pattern established by scripts/hello.py. Ensure compatibility with the uv script runner used throughout the project.

### Phase 2: Core Implementation
Implement the `goodbye()` function with a clean, simple design that mirrors the hello() function. Add a CLI interface using Python's argparse module to allow standalone execution. Include a main block for direct execution.

### Phase 3: Integration
Make the script executable and validate it works correctly. Ensure the implementation is consistent with the existing hello.py script.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Create the goodbye.py script structure
**Status:** complete
- Create `scripts/goodbye.py` with proper Python shebang (`#!/usr/bin/env -S uv run --script`)
- Add inline uv script dependencies block (same format as hello.py with empty dependencies)
- Add module-level docstring explaining the script's purpose, usage examples, and how it mirrors the hello function

### Implement the goodbye function
**Status:** complete
- Define `goodbye()` function that prints 'Goodbye World' to stdout
- Use a simple `print('Goodbye World')` statement
- Add a comprehensive docstring to the function explaining what it does

### Add CLI interface
**Status:** complete
- Add argument parser using argparse module (same pattern as hello.py)
- Support `--help` flag showing usage information
- Create main() function that parses args and calls goodbye()
- Add `if __name__ == "__main__":` block to invoke main()

### Make the script executable
**Status:** complete
- Add executable permissions using `chmod +x scripts/goodbye.py`
- Verify the script can be executed directly

### Run validation commands
**Status:** complete
- Execute all validation commands listed below to confirm the function works correctly with zero errors

## Testing Strategy
### Unit Tests
- Test that goodbye() function prints exactly 'Goodbye World'
- Test that the script executes without errors
- Test that --help flag displays usage information
- Test direct execution via `python scripts/goodbye.py`
- Test execution via `./scripts/goodbye.py` (with shebang)
- Test execution via `uv run --script scripts/goodbye.py`

### Edge Cases
- Script execution without Python in PATH (should fail gracefully with the shebang)
- Multiple invocations (should print 'Goodbye World' each time)
- Script import as module (should not auto-execute, only when called)

## Acceptance Criteria
- A `goodbye()` function exists that prints 'Goodbye World'
- The function is defined in `scripts/goodbye.py`
- The script can be executed directly: `./scripts/goodbye.py`
- The script can be executed with Python: `python3 scripts/goodbye.py`
- The script can be executed with uv: `uv run --script scripts/goodbye.py`
- The script shows help with `./scripts/goodbye.py --help`
- The script prints exactly 'Goodbye World' when executed
- The script follows the exact same pattern as scripts/hello.py (structure, shebang, documentation)
- All validation commands pass without errors

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Verify the script was created
ls -la scripts/goodbye.py

# Verify the script is executable
test -x scripts/goodbye.py && echo "Script is executable"

# Verify Python syntax is valid
python3 -m py_compile scripts/goodbye.py

# Test help output
python3 scripts/goodbye.py --help

# Test the goodbye function prints "Goodbye World"
python3 scripts/goodbye.py | grep -q "Goodbye World" && echo "Output is correct"

# Test direct execution (if executable)
./scripts/goodbye.py | grep -q "Goodbye World" && echo "Direct execution works"

# Test uv compatibility
uv run --script scripts/goodbye.py | grep -q "Goodbye World" && echo "uv execution works"

# Verify both hello and goodbye work (no regressions)
python3 scripts/hello.py | grep -q "Hello World" && echo "Hello function still works"
./scripts/hello.py | grep -q "Hello World" && echo "Hello direct execution still works"
```

## Notes
- This function intentionally mirrors the hello.py implementation for consistency
- The function serves as another example utility and demonstrates consistent patterns
- No external dependencies are needed for this function
- The script follows the uv inline script pattern used throughout the project
- Future enhancements could add parameters to customize the farewell message
- This function is primarily for demonstration/example purposes rather than production use
- The implementation should be nearly identical to hello.py, just with different output text
