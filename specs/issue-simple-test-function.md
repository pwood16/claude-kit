# Feature: Simple Test Function

## Feature Description
Add a simple, reusable "test" function that performs basic assertions and validations to demonstrate testing patterns and serve as a minimal example test utility. This function will be implemented as a standalone Python script in the scripts directory, providing a foundation for testing utilities and demonstrating assertion patterns in the project.

## User Story
As a developer
I want a simple test function that performs basic checks and assertions
So that I can have a basic testing utility for validation, examples, and as a template for other test utilities

## Problem Statement
The claude-kit project has example utility functions (hello.py, goodbye.py) but lacks a simple test function that demonstrates assertion and validation patterns. While the project has test fixtures in the test/ directory, there's no basic example function that shows how to implement simple checks and validations. This makes it harder for contributors to understand patterns for adding test utilities.

## Solution Statement
Create a simple Python script with a `test()` function that performs basic assertions and prints test results. The script will:
1. Define a clean, callable `test()` function
2. Perform simple assertions (e.g., 1 + 1 == 2, string comparisons)
3. Print test results to stdout
4. Be executable from the command line
5. Follow the project's existing patterns (uv-compatible, properly structured)
6. Include a simple CLI interface for standalone execution
7. Serve as a minimal example for test utility development

## Relevant Files
Use these files to implement the feature:

- `scripts/hello.py` - Existing utility script demonstrating the pattern to follow for structure, shebang, and CLI interface
- `scripts/goodbye.py` - Another example utility showing consistent implementation patterns
- `test/README.md` - Documentation about testing fixtures and patterns

### New Files
- `scripts/test.py` - The test function implementation as a standalone Python script

## Implementation Plan
### Phase 1: Foundation
Create the basic script structure with proper shebang and imports, following the pattern established by hello.py and goodbye.py. Ensure compatibility with the uv script runner used throughout the project.

### Phase 2: Core Implementation
Implement the `test()` function with simple assertions and test cases. The function should:
- Run multiple basic test assertions (arithmetic, string comparison, boolean logic)
- Track pass/fail status for each test
- Print results in a clear format
- Return an exit code indicating overall success/failure

### Phase 3: Integration
Make the script executable, validate it works correctly, and ensure it follows the same patterns as other utility scripts in the project.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Create the test.py script structure
**Status:** complete
- Create `scripts/test.py` with proper Python shebang using uv
- Add inline uv script dependencies block (empty, as no external dependencies needed)
- Add module docstring explaining the script's purpose and usage

### Implement the test function
- Define `test()` function that runs simple assertions
- Include test cases for:
  - Arithmetic operations (1 + 1 == 2)
  - String comparisons ('test' == 'test')
  - Boolean logic (True and True == True)
  - List operations ([1, 2, 3] == [1, 2, 3])
- Track and count passing vs failing tests
- Print results in a clear, readable format showing each test
- Return boolean indicating if all tests passed

### Add CLI interface
- Add argument parser using argparse module
- Support `--help` flag showing usage information
- Support optional `--verbose` flag for detailed output
- Create main() function that calls test()
- Add `if __name__ == "__main__":` block to invoke main()
- Set exit code based on test results (0 for success, 1 for failure)

### Make the script executable
- Add executable permissions using `chmod +x scripts/test.py`
- Verify the script can be executed directly with proper shebang

### Run validation commands
- Execute all validation commands listed below to confirm the function works correctly with zero errors

## Testing Strategy
### Unit Tests
- Test that test() function executes all assertions
- Test that passing assertions are counted correctly
- Test that the script returns exit code 0 when all tests pass
- Test that the script executes without errors
- Test that --help flag displays usage information
- Test that --verbose flag provides detailed output
- Test direct execution via `python scripts/test.py`
- Test execution via `./scripts/test.py` (with shebang)
- Test execution via `uv run --script scripts/test.py`

### Edge Cases
- Script execution without Python in PATH (should fail gracefully)
- Multiple invocations (should produce consistent results)
- Script import as module (should not auto-execute, only when called)

## Acceptance Criteria
- A `test()` function exists that runs simple assertions
- The function is defined in `scripts/test.py`
- The script can be executed directly: `./scripts/test.py`
- The script can be executed with Python: `python scripts/test.py`
- The script can be executed with uv: `uv run --script scripts/test.py`
- The script shows help with `./scripts/test.py --help`
- The script runs multiple test assertions and reports results
- The script returns exit code 0 when all tests pass
- The script returns exit code 1 if any test fails
- The script follows project conventions (shebang, structure, patterns from hello.py/goodbye.py)
- All validation commands pass without errors

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Verify the script was created
ls -la scripts/test.py

# Verify the script is executable
test -x scripts/test.py && echo "Script is executable"

# Verify Python syntax is valid
python3 -m py_compile scripts/test.py

# Test help output
python3 scripts/test.py --help

# Test the test function runs successfully
python3 scripts/test.py && echo "Tests passed"

# Test direct execution (if executable)
./scripts/test.py && echo "Direct execution works"

# Test uv compatibility
uv run --script scripts/test.py && echo "uv execution works"

# Test verbose output
python3 scripts/test.py --verbose

# Verify exit code on success
python3 scripts/test.py; test $? -eq 0 && echo "Exit code is correct"
```

## Notes
- This is intentionally minimal - a simple test function should be straightforward
- The function demonstrates basic assertion patterns that can be expanded
- No external testing frameworks (pytest, unittest) are used to keep it simple
- The script follows the uv inline script pattern used in hello.py and goodbye.py
- The test assertions are deliberately simple and will always pass to demonstrate the pattern
- Future enhancements could:
  - Add parameterized tests
  - Support test discovery
  - Add test fixtures
  - Integrate with pytest or other frameworks
- This function is primarily for demonstration/example purposes
- Can be used as a quick sanity check that Python environment is working correctly
