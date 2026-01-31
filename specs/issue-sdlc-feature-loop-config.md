# Feature: Configuration File Support for feature-loop Script

## Feature Description
Add support for a `.claude-kit` configuration file that allows users to customize default behavior of the feature-loop script without passing command-line arguments every time. The configuration file should support all current CLI parameters plus extensibility for future ACR-related parameters (like number of reviewers). Command-line arguments should override configuration file values, providing a flexible hierarchy of defaults.

## User Story
As a developer using the feature-loop script
I want to configure default behavior in a `.claude-kit` file
So that I don't have to repeatedly pass the same command-line arguments and can maintain consistent settings across my project or organization.

## Problem Statement
Currently, the feature-loop script requires users to pass command-line arguments for every invocation if they want non-default behavior. Users who consistently want different settings (e.g., 3 review iterations instead of 5, or specific ACR configurations) must remember and type these flags every time. This creates friction and inconsistency across team members who may have different preferences or project-specific requirements.

## Solution Statement
Implement a configuration file system that:
1. Reads from `.claude-kit` configuration files in JSON, YAML, or TOML format (prioritize JSON for simplicity)
2. Searches for config files in multiple locations (current directory, project root, home directory)
3. Merges configurations with precedence: CLI args > project config > user config > defaults
4. Supports all current CLI parameters plus extensible ACR parameters
5. Validates configuration and provides helpful error messages for invalid settings
6. Documents the configuration schema and available options

## Relevant Files
Use these files to implement the feature:

- `plugins/sdlc/scripts/feature-loop` - Main script that needs configuration loading
  - Currently has hardcoded defaults and argparse configuration
  - Will need to load and merge configuration from file(s)
  - CLI argument handling remains but becomes override mechanism

- `plugins/sdlc/README.md` - Documentation for the SDLC plugin
  - Needs section documenting the configuration file format
  - Should include examples of common configurations
  - Should document the precedence order and search paths

### New Files

- `.claude-kit.example` - Example configuration file template
  - Documents all available configuration options
  - Includes comments explaining each setting
  - Can be copied by users to get started

- `plugins/sdlc/scripts/config_loader.py` - Configuration loading module (optional)
  - If the logic becomes complex, extract to separate module
  - Handles file discovery, parsing, merging, and validation

## Implementation Plan

### Phase 1: Foundation
Design the configuration schema and file format. Determine which format to use (JSON recommended for zero dependencies) and define the structure that supports current parameters plus extensibility. Establish the configuration precedence hierarchy and file search locations.

### Phase 2: Core Implementation
Implement configuration file loading in the feature-loop script. Add logic to discover and parse configuration files from multiple locations, merge them according to precedence rules, and integrate with existing argparse logic so CLI arguments override config file values.

### Phase 3: Integration
Update the argument parsing and default value handling to use configuration values. Add validation for configuration settings and provide helpful error messages. Create example configuration file and update documentation.

## Step by Step Tasks

### Research Existing Configuration Patterns
- Search the codebase for existing configuration file patterns in other plugins
- Check if there are established conventions for configuration in Claude Code plugins
- Document findings and determine if we should follow existing patterns

### Define Configuration Schema
- Design JSON schema for `.claude-kit` configuration file
- Define structure supporting current parameters: `max_review_iterations`, `skip_review`, `verbose`
- Add extensible section for future ACR parameters: `acr.num_reviewers`, `acr.review_style`, etc.
- Document the schema with comments explaining each field

### Implement Configuration Discovery
- Add function to search for `.claude-kit` files in multiple locations:
  1. Current working directory (`./.claude-kit`)
  2. Git root directory (if in a git repo)
  3. User home directory (`~/.claude-kit`)
- Implement logic to detect and handle missing config files gracefully
- Add verbose logging to show which config files were found and loaded

### Implement Configuration Parser
- Add JSON parsing with error handling for malformed files
- Implement configuration validation to ensure values are correct types and within valid ranges
- Provide helpful error messages for invalid configurations (e.g., "max_review_iterations must be a positive integer")

### Implement Configuration Merging
- Create merge logic that combines configs with proper precedence:
  1. Hardcoded defaults (lowest priority)
  2. User home directory config
  3. Project config (git root or current directory)
  4. CLI arguments (highest priority)
- Handle partial configurations (not all fields need to be specified)
- Ensure CLI arguments always win over config file values

### Integrate with Argument Parser
- Modify argparse setup to use configuration values as defaults instead of hardcoded values
- Ensure --help output shows the effective defaults based on loaded config
- Keep all existing CLI arguments working as before

### Add Verbose Configuration Logging
- When `--verbose` is enabled, log which configuration files were loaded
- Show the effective configuration being used (after merging)
- Display which settings came from which source (default, config file, or CLI)

### Create Example Configuration File
- Create `.claude-kit.example` with all available options documented
- Add inline comments explaining each setting and its valid values
- Include examples of common configurations (e.g., fast mode, thorough mode)
- Add to git repository as reference for users

### Update Documentation
- Add "Configuration" section to `plugins/sdlc/README.md`
- Document the configuration file format with complete example
- Explain the precedence order and file search locations
- Provide examples of common use cases and configurations
- Document all available configuration options

### Add Tests for Configuration Loading
- Create test configuration files with various scenarios
- Test configuration discovery from different locations
- Test precedence order (CLI > project > user > defaults)
- Test error handling for malformed JSON and invalid values
- Test partial configurations and missing files

### Validate Feature Works End-to-End
- Create a sample `.claude-kit` file with custom settings
- Run feature-loop without CLI args and verify it uses config values
- Run feature-loop with CLI args and verify they override config values
- Test with missing config file and verify defaults are used
- Run with `--verbose` and verify configuration loading is logged properly
- Execute validation commands to ensure zero regressions

## Testing Strategy

### Unit Tests
- Test configuration file discovery in various directory structures
- Test JSON parsing with valid and invalid inputs
- Test configuration merging with various precedence scenarios
- Test validation logic for all configuration fields
- Test error messages are helpful and actionable

### Integration Tests
- Test feature-loop with configuration file in different locations
- Test CLI argument override behavior
- Test with partial configuration files
- Test with no configuration file present
- Test verbose logging output

### Edge Cases
- Empty configuration file
- Configuration file with only comments (if JSON5/JSONC support added)
- Configuration file with unknown/extra fields (should be ignored or warned)
- Configuration file with wrong types (string instead of number, etc.)
- Configuration file with out-of-range values (negative iterations, etc.)
- Multiple configuration files at different levels
- Configuration file with Unicode or special characters
- Very large iteration counts or other extreme values
- Configuration file with only some fields specified
- Symlinked configuration files

## Acceptance Criteria

1. Users can create a `.claude-kit` file in their project root with configuration settings
2. The feature-loop script reads and applies configuration from the file
3. CLI arguments override configuration file values when specified
4. Configuration files can be placed in current directory, git root, or home directory
5. The script provides clear error messages for invalid configuration
6. Documentation includes complete configuration reference with examples
7. The `--verbose` flag shows which configuration files were loaded and the effective settings
8. All existing CLI arguments continue to work exactly as before
9. The script works correctly when no configuration file is present (backwards compatibility)
10. Example configuration file (`.claude-kit.example`) is provided in the repository

## Validation Commands

Execute every command to validate the feature works correctly with zero regressions.

```bash
# 1. Verify the example config file exists and is valid JSON
cat .claude-kit.example
python3 -c "import json; json.load(open('.claude-kit.example'))"

# 2. Test feature-loop without config file (ensure backwards compatibility)
rm -f .claude-kit
./plugins/sdlc/scripts/feature-loop --help

# 3. Create a test config file with custom settings
cat > .claude-kit << 'EOF'
{
  "feature_loop": {
    "max_review_iterations": 3,
    "skip_review": false,
    "verbose": true
  }
}
EOF

# 4. Test that config file is loaded (use --verbose to see)
./plugins/sdlc/scripts/feature-loop --help

# 5. Test CLI override (should use 10 instead of 3 from config)
# (Don't actually run a full loop, just verify args are parsed correctly)
./plugins/sdlc/scripts/feature-loop --prompt "test" --max-review-iterations 10 --skip-review 2>&1 | head -20

# 6. Test invalid config file handling
echo "invalid json" > .claude-kit
./plugins/sdlc/scripts/feature-loop --help 2>&1 | grep -i "error\|invalid"

# 7. Clean up test files
rm -f .claude-kit

# 8. Verify documentation is updated
grep -A 10 "Configuration" plugins/sdlc/README.md

# 9. Run syntax check on the Python script
python3 -m py_compile plugins/sdlc/scripts/feature-loop

# 10. Test with example config copied
cp .claude-kit.example .claude-kit
./plugins/sdlc/scripts/feature-loop --help
rm -f .claude-kit
```

## Notes

### Configuration File Format Choice
JSON is recommended over YAML or TOML because:
- Zero dependencies (Python standard library has `json` module)
- Consistent with existing `.claude-plugin/plugin.json` files
- Simple and widely understood
- Good error messages for parsing issues

If YAML support is desired later, it can be added as an optional enhancement using PyYAML library.

### Extensibility Considerations
The configuration schema should be designed with extensibility in mind:
- Use nested structures for related settings (e.g., `acr.num_reviewers`)
- Document that unknown fields are ignored (allows forward compatibility)
- Version the configuration schema if breaking changes are needed later

### Future ACR Parameters
Potential future configuration options to consider:
- `acr.num_reviewers`: Number of reviewers to use (default: 1)
- `acr.review_style`: Style of review (e.g., "strict", "normal", "lenient")
- `acr.auto_fix`: Whether to automatically fix issues vs. just report
- `acr.exclude_patterns`: File patterns to exclude from review
- `acr.custom_rules`: Path to custom review rules file

### Configuration Hierarchy Example
```
Effective value = CLI arg || Project config || User config || Default

# Example precedence:
max_review_iterations = 10 (from CLI --max-review-iterations 10)
skip_review = false (from ./.claude-kit)
verbose = true (from ~/.claude-kit)
```

### Home Directory Config Use Case
A `~/.claude-kit` file allows users to set personal preferences across all projects:
```json
{
  "feature_loop": {
    "verbose": true,
    "max_review_iterations": 3
  }
}
```

### Project Config Use Case
A `./.claude-kit` file in the project root sets team-wide standards:
```json
{
  "feature_loop": {
    "max_review_iterations": 5,
    "skip_review": false
  },
  "acr": {
    "num_reviewers": 2,
    "review_style": "strict"
  }
}
```
