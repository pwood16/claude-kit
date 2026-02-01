# Feature: Simple Hello World Function

## Feature Description
Add a simple, standalone hello world function that prints 'Hello World' to stdout as a new Python script. This function will serve as a minimal example utility and demonstrate the basic patterns for adding simple functions to the claude-kit project. The function will be implemented following the established conventions for Python scripts in this codebase.

## User Story
As a developer
I want to add a simple hello world function to a new file
So that I can demonstrate basic function implementation patterns and have a template for creating simple utilities

## Problem Statement
While the claude-kit project has several utility scripts (hello.py, goodbye.py, test.py), there's value in documenting the process of adding a new simple function from scratch. This demonstrates to contributors how to add new utilities following the project's conventions for script structure, documentation, and testing.

## Solution Statement
Create a new Python script named `simple_hello.py` in the `scripts/` directory with:
1. A `simple_hello()` function that prints 'Hello World'
2. Proper uv-compatible script structure with shebang and metadata
3. A CLI interface using argparse for standalone execution
4. Comprehensive docstrings following the existing pattern
5. Executable permissions for direct invocation

The implementation will mirror the patterns established in `hello.py`, `goodbye.py`, and `test.py`.

## Relevant Files
Use these files to implement the feature:

- `scripts/hello.py` - Provides the template pattern for simple utility scripts (shebang, uv metadata, argparse, docstrings)
- `scripts/goodbye.py` - Demonstrates consistent implementation patterns across similar utilities
- `scripts/test.py` - Shows more complex CLI argument handling with flags

### New Files
- `scripts/simple_hello.py` - The new hello world function implementation as a standalone Python script

## Implementation Plan
### Phase 1: Foundation
Create the basic script structure with proper shebang, uv script metadata block, and module-level docstring. The structure will follow the exact pattern used in existing scripts to ensure consistency.

### Phase 2: Core Implementation
Implement the `simple_hello()` function with a clean, minimal design that prints 'Hello World' to stdout. Add a complete CLI interface using argparse with help documentation, and include a main() function that serves as the entry point.

### Phase 3: Integration
Make the script executable with proper permissions, validate it works correctly through multiple execution methods (direct, python, uv), and ensure it follows all project conventions.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Create the simple_hello.py script file
**Status:** complete
- Create new file `scripts/simple_hello.py` with proper Python shebang: `#!/usr/bin/env -S uv run --script`
- Add uv script metadata block with Python version requirement and empty dependencies list
- Add comprehensive module-level docstring explaining purpose, usage examples, and execution methods

### Implement the simple_hello function
**Status:** complete
- Define `simple_hello()` function with proper type hint (`-> None`)
- Implement function body with single `print('Hello World')` statement
- Add detailed function-level docstring explaining what it does

### Add CLI interface and main entry point
**Status:** complete
- Import argparse module at top of file
- Create `main()` function with type hint (`-> None`)
- Initialize ArgumentParser with description and RawDescriptionHelpFormatter
- Call `parser.parse_args()` to enable --help flag
- Call `simple_hello()` function from main
- Add `if __name__ == "__main__":` guard block that calls `main()`

### Make the script executable
**Status:** complete
- Use `chmod +x scripts/simple_hello.py` to add executable permissions
- Verify executable bit is set with `ls -la scripts/simple_hello.py`

### Validate the implementation
**Status:** complete
- Run all validation commands listed below to ensure the function works correctly
- Confirm zero errors across all execution methods
- Verify output matches expected 'Hello World' exactly

## Testing Strategy
### Unit Tests
- Test that simple_hello() function prints exactly 'Hello World' to stdout
- Test that script executes without errors via `python3 scripts/simple_hello.py`
- Test that script executes without errors via `./scripts/simple_hello.py`
- Test that script executes without errors via `uv run --script scripts/simple_hello.py`
- Test that --help flag displays properly formatted usage information
- Test Python syntax is valid with py_compile module

### Edge Cases
- Script execution when imported as a module (should not auto-execute)
- Multiple consecutive invocations (should print 'Hello World' each time consistently)
- Output redirection to file or pipe (should work correctly)
- Script execution without uv available (should work with standard Python)

## Acceptance Criteria
- A `simple_hello()` function exists in `scripts/simple_hello.py`
- The function prints exactly 'Hello World' when called
- The script can be executed directly: `./scripts/simple_hello.py`
- The script can be executed with Python: `python3 scripts/simple_hello.py`
- The script can be executed with uv: `uv run --script scripts/simple_hello.py`
- The script shows help documentation with `--help` flag
- The script has executable permissions set
- The script follows all project conventions: shebang, uv metadata, docstrings, type hints
- All validation commands execute successfully with zero errors
- Output is clean with no warnings or errors

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Verify the script file was created
ls -la scripts/simple_hello.py

# Verify the script is executable
test -x scripts/simple_hello.py && echo "✓ Script is executable"

# Verify Python syntax is valid
python3 -m py_compile scripts/simple_hello.py && echo "✓ Python syntax is valid"

# Test help output displays correctly
python3 scripts/simple_hello.py --help

# Test execution with python3 - verify output
python3 scripts/simple_hello.py

# Test execution with python3 - verify exact output
python3 scripts/simple_hello.py | grep -q "Hello World" && echo "✓ Python execution works correctly"

# Test direct execution (shebang)
./scripts/simple_hello.py

# Test direct execution - verify exact output
./scripts/simple_hello.py | grep -q "Hello World" && echo "✓ Direct execution works correctly"

# Test uv execution
uv run --script scripts/simple_hello.py

# Test uv execution - verify exact output
uv run --script scripts/simple_hello.py | grep -q "Hello World" && echo "✓ UV execution works correctly"

# Verify all execution methods produce identical output
diff <(python3 scripts/simple_hello.py) <(./scripts/simple_hello.py) && echo "✓ All execution methods produce identical output"
```

## Notes
- This function intentionally mirrors `hello.py` but with a different name to demonstrate adding a new file from scratch
- The implementation serves as a documented example of the minimal requirements for adding utility scripts
- No external dependencies are required - uses only Python standard library
- The uv script metadata pattern ensures compatibility with the project's dependency management
- Future contributors can reference this spec to understand the complete process for adding simple utilities
- The script name `simple_hello.py` differentiates it from the existing `hello.py` while maintaining clarity
- This is a demonstration/template utility rather than production functionality
