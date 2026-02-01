#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
ralph-loop - Run a Ralph Wiggum loop on a spec file.

Iteratively runs claude -p to work through spec tasks until complete.
Supports two spec formats:
  1. Markdown specs with "## Step by Step Tasks" section (h3 headers as tasks)
  2. JSON PRD files with a "stories" array (legacy format)

Exits when: all tasks complete, max-iterations reached, or completion promise detected.

Usage:
    ralph-loop --spec <file> [--max-iterations N] [--model MODEL] [--log FILE]
    ralph-loop --prd <file> [--max-iterations N] [--completion-promise TEXT]  (legacy JSON format)

Examples:
    ralph-loop --spec specs/feature.md
    ralph-loop --spec specs/feature.json --max-iterations 10
    ralph-loop --prd legacy.json --completion-promise "ALL DONE"
    ralph-loop --spec specs/feature.md --model claude --log /tmp/ralph.log
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Import structured logger
try:
    from lib.logger import StructuredLogger
except ImportError:
    # Handle case where lib is not in the path
    import sys
    from pathlib import Path
    script_dir = Path(__file__).parent
    lib_dir = script_dir.parent / "lib"
    sys.path.insert(0, str(lib_dir))
    from logger import StructuredLogger


def log(step: str, message: str) -> None:
    """Log a message with step indicator."""
    print(f"[{step}] {message}", flush=True)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run a Ralph Wiggum loop on a spec file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Supports two spec formats:
  1. Markdown specs with "## Step by Step Tasks" section (h3 headers as tasks)
  2. JSON PRD files with a "stories" array (legacy format)

Examples:
    %(prog)s --spec specs/feature.md
    %(prog)s --spec specs/feature.json --max-iterations 10
    %(prog)s --prd legacy.json --completion-promise "ALL DONE"
    %(prog)s --spec specs/feature.md --model claude --log /tmp/ralph.log
        """
    )

    # Create mutually exclusive group for --spec and --prd (both do the same thing)
    spec_group = parser.add_mutually_exclusive_group(required=True)
    spec_group.add_argument(
        "--spec",
        dest="spec_file",
        help="Path to spec file (Markdown or JSON)"
    )
    spec_group.add_argument(
        "--prd",
        dest="spec_file",
        help="Path to spec file (legacy alias for --spec)"
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=0,
        help="Maximum iterations (0 = unlimited, default: 0)"
    )
    parser.add_argument(
        "--completion-promise",
        default="TASK COMPLETE",
        help='String to detect completion (default: "TASK COMPLETE")'
    )
    parser.add_argument(
        "--model",
        type=str,
        default="claude",
        help="Model to use for agent invocations (default: claude)"
    )
    parser.add_argument(
        "--log",
        "--log-file",
        dest="log_file",
        type=str,
        default=None,
        help="Path to log file for detailed execution capture (optional)"
    )

    args = parser.parse_args()

    # Validate spec file exists
    spec_path = Path(args.spec_file)
    if not spec_path.exists():
        parser.error(f"Spec file not found: {args.spec_file}")

    if not spec_path.is_file():
        parser.error(f"Spec path is not a file: {args.spec_file}")

    return args


def detect_spec_format(spec_file: Path) -> str:
    """
    Detect spec format based on file extension and content.

    Returns: "json" or "markdown"
    Raises: ValueError if format cannot be determined
    """
    # Check file extension first
    suffix = spec_file.suffix.lower()

    if suffix == ".json":
        return "json"
    elif suffix == ".md":
        return "markdown"

    # Try to auto-detect based on content
    content = spec_file.read_text()

    # Try parsing as JSON
    try:
        data = json.loads(content)
        if isinstance(data, dict) and "stories" in data:
            return "json"
    except json.JSONDecodeError:
        pass

    # Check for markdown markers
    if re.search(r"^## Step by Step Tasks", content, re.MULTILINE):
        return "markdown"

    raise ValueError(
        f"Could not detect spec format for: {spec_file}\n"
        "Use .json or .md extension, or ensure the file contains "
        "a 'stories' array (JSON) or '## Step by Step Tasks' section (Markdown)."
    )


def validate_json_spec(spec_file: Path) -> None:
    """
    Validate that a JSON spec file has a 'stories' array.

    Raises: ValueError if validation fails
    """
    try:
        content = spec_file.read_text()
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in spec file: {e}")

    if not isinstance(data, dict):
        raise ValueError("JSON spec must be an object with a 'stories' array")

    if "stories" not in data:
        raise ValueError("JSON spec must have a 'stories' array")

    if not isinstance(data["stories"], list):
        raise ValueError("'stories' must be an array")


def validate_markdown_spec(spec_file: Path) -> None:
    """
    Validate that a Markdown spec file has a '## Step by Step Tasks' section.

    Raises: ValueError if validation fails
    """
    content = spec_file.read_text()

    if not re.search(r"^## Step by Step Tasks", content, re.MULTILINE):
        raise ValueError(
            f"Markdown spec must have '## Step by Step Tasks' section: {spec_file}"
        )


def initialize_progress_file(spec_file: Path) -> Path:
    """
    Initialize progress file if it doesn't exist.

    Returns: Path to progress file
    """
    spec_name = spec_file.stem  # basename without extension
    progress_file = Path(f"{spec_name}-progress.txt")

    if not progress_file.exists():
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"""# Progress Log for {spec_name}
# Started: {timestamp}

"""
        progress_file.write_text(content)

    return progress_file


def check_json_completion(spec_file: Path) -> int:
    """
    Count incomplete stories in a JSON spec.

    Returns: Number of pending (incomplete) stories
    """
    try:
        content = spec_file.read_text()
        data = json.loads(content)
    except (json.JSONDecodeError, OSError) as e:
        log("ERROR", f"Failed to parse spec file: {e}")
        sys.exit(1)

    stories = data.get("stories", [])
    pending = 0

    for story in stories:
        status = story.get("status", "").lower()
        if status not in ("complete", "done"):
            pending += 1

    return pending


def check_markdown_completion(spec_file: Path) -> int:
    """
    Count incomplete tasks in a Markdown spec.

    Looks for h3 headers in the '## Step by Step Tasks' section
    that are NOT followed by '**Status:** complete'.

    Returns: Number of pending (incomplete) tasks
    """
    content = spec_file.read_text()
    lines = content.split("\n")

    in_tasks = False
    pending = 0
    prev_was_h3 = False

    for line in lines:
        # Check for entering Step by Step Tasks section
        if line.startswith("## Step by Step Tasks"):
            in_tasks = True
            continue

        # Check for exiting section (hit another h2)
        if in_tasks and line.startswith("## ") and not line.startswith("## Step by Step Tasks"):
            break

        if in_tasks:
            if line.startswith("### "):
                # Found a task header, assume incomplete until we check next line
                prev_was_h3 = True
                pending += 1
            elif prev_was_h3:
                # Check if this line marks completion
                if "**Status:**" in line and "complete" in line.lower():
                    pending -= 1
                prev_was_h3 = False

    return pending


def generate_json_prompt(spec_basename: str, progress_file: Path, completion_promise: str) -> str:
    """Generate the iteration prompt for JSON format specs."""
    return f"""# Ralph Wiggum Loop - Iteration Prompt

You are an autonomous AI agent working through a spec to complete all stories.

## Your Task

1. Read `{spec_basename}` to understand the stories and their status
2. Read `{progress_file}` to understand what has been learned in previous iterations
3. Select the highest-priority incomplete story that is not blocked
4. Implement the story completely
5. Update `{spec_basename}` to mark the story with `"status": "complete"` when done
6. Append learnings to `{progress_file}`

## Important Rules

- **One story per iteration**: Focus on completing one story fully before moving to the next
- **Update the spec file**: When a story is complete, set `"status": "complete"`
- **Append to progress file**: Document what you did, any issues encountered, and learnings
- **Stay focused**: Only work on stories in this spec, ignore other specs
- **Completion promise**: When all stories are complete, output exactly: `{completion_promise}`

## Story Priority Order

1. First, complete all P0 stories (highest priority)
2. Then, complete P1 stories
3. Then, complete P2 stories
4. Respect `blocked_by` dependencies - don't start a story until its dependencies are complete

## Verification

Before marking a story as complete:
- All acceptance criteria met
- Code compiles/lints without errors
- No obvious errors in the implementation

## Begin

Read `{spec_basename}` and `{progress_file}` now, then implement the next incomplete story."""


def generate_markdown_prompt(spec_basename: str, progress_file: Path, completion_promise: str) -> str:
    """Generate the iteration prompt for Markdown format specs."""
    return f"""# Ralph Wiggum Loop - Iteration Prompt

You are an autonomous AI agent working through a feature spec to complete all tasks.

## Your Task

1. Read `{spec_basename}` to understand the feature and the Step by Step Tasks
2. Read `{progress_file}` to understand what has been done in previous iterations
3. Find the first incomplete task (a task without `**Status:** complete` after its heading)
4. Implement that task completely
5. Update `{spec_basename}` to mark the task as complete by adding `**Status:** complete` on the line after the h3 heading
6. Append learnings to `{progress_file}`

## Important Rules

- **One task per iteration**: Focus on completing one task fully before moving to the next
- **Execute tasks in order**: Work through tasks from top to bottom as listed in the spec
- **Mark completion**: After the h3 task heading, add a line: `**Status:** complete`
- **Append to progress file**: Document what you did, any issues encountered, and learnings
- **Stay focused**: Only work on tasks in this spec
- **Completion promise**: When all tasks are complete, output exactly: `{completion_promise}`

## Task Status Format

When a task is incomplete, it looks like:
```
### Step 1: Create the database schema
- Create migrations for users table
- Add indexes
```

When you complete it, add the status line:
```
### Step 1: Create the database schema
**Status:** complete
- Create migrations for users table
- Add indexes
```

## Verification

Before marking a task as complete:
- All bullet points under the task are done
- Code compiles/lints without errors
- No obvious errors in the implementation

## Begin

Read `{spec_basename}` and `{progress_file}` now, then implement the next incomplete task."""


def check_completion_promise(output: str, promise: str) -> bool:
    """Check if the completion promise appears in the output."""
    return promise in output


def run_claude_iteration(
    prompt: str,
    progress_file: Path,
    iteration: int,
    model: str = "claude",
    logger: Optional[StructuredLogger] = None
) -> tuple[int, str]:
    """
    Run a single Claude iteration with the given prompt.

    Args:
        prompt: The prompt to send to Claude
        progress_file: Path to the progress file
        iteration: Current iteration number
        model: Model to use for the invocation (default: "claude")
        logger: Optional StructuredLogger for detailed logging

    Returns: (exit_code, output)
    """
    cmd = [model, "--dangerously-skip-permissions", "--verbose", "-p", prompt]

    # Log command execution start
    if logger:
        logger.log_command(cmd, output="", exit_code=0, duration=0.0,
                          iteration=iteration, phase="start")

    start_time = time.time()

    # Create temp file to capture output while also streaming it
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Run command with tee-like behavior
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        output_lines = []
        with open(tmp_path, "w") as tmp_file:
            for line in process.stdout:
                print(line, end="", flush=True)
                tmp_file.write(line)
                output_lines.append(line)

        process.wait()
        output = "".join(output_lines)
        duration = time.time() - start_time

        # Log command execution completion
        if logger:
            logger.log_command(cmd, output=output, exit_code=process.returncode,
                              duration=duration, iteration=iteration)

        return process.returncode, output
    except Exception as e:
        duration = time.time() - start_time
        # Log error
        if logger:
            logger.log_error("command_execution_error", str(e),
                           command=cmd, iteration=iteration, duration=duration)
        raise
    finally:
        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def commit_changes(spec_name: str, iteration: int) -> None:
    """Commit any uncommitted changes with an iteration-specific message."""
    # Check if there are uncommitted changes
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True
    )

    if not result.stdout.strip():
        # No changes to commit
        return

    print("Committing changes...")

    # Stage all changes
    subprocess.run(["git", "add", "-A"], check=False)

    # Create commit message
    commit_message = f"""[{spec_name}] Ralph iteration {iteration}

Co-Authored-By: Claude <noreply@anthropic.com>"""

    # Commit changes (don't fail if commit fails)
    subprocess.run(
        ["git", "commit", "-m", commit_message],
        check=False,
        capture_output=True
    )


def run_ralph_loop(args: argparse.Namespace) -> int:
    """Main Ralph loop logic."""
    spec_file = Path(args.spec_file)
    max_iterations = args.max_iterations
    completion_promise = args.completion_promise
    model = args.model
    log_file = args.log_file

    # Initialize logger if log file is specified
    logger = None
    if log_file:
        try:
            logger = StructuredLogger(log_file)
            log("INIT", f"Logging enabled: {log_file}")
        except Exception as e:
            log("WARNING", f"Failed to initialize logger: {e}")
            log("WARNING", "Continuing without logging")

    # Detect and validate spec format
    try:
        spec_format = detect_spec_format(spec_file)
    except ValueError as e:
        log("ERROR", str(e))
        if logger:
            logger.log_error("spec_format_error", str(e))
        return 1

    # Validate spec file
    try:
        if spec_format == "json":
            validate_json_spec(spec_file)
        else:
            validate_markdown_spec(spec_file)
    except ValueError as e:
        log("ERROR", str(e))
        if logger:
            logger.log_error("spec_validation_error", str(e))
        return 1

    # Initialize progress file
    progress_file = initialize_progress_file(spec_file)

    spec_basename = spec_file.name
    spec_name = spec_file.stem

    # Log configuration snapshot
    if logger:
        logger.log_configuration({
            "spec_file": str(spec_file),
            "spec_format": spec_format,
            "max_iterations": max_iterations,
            "completion_promise": completion_promise,
            "model": model,
            "log_file": log_file
        })

    # Print header
    print("======================================")
    print("  Ralph Wiggum Loop")
    print("======================================")
    print()
    print(f"Spec file:          {spec_basename}")
    print(f"Spec format:        {spec_format}")
    print(f"Progress file:      {progress_file}")
    print(f"Max iterations:     {max_iterations}")
    print(f"Completion promise: {completion_promise}")
    print(f"Model:              {model}")
    if log_file:
        print(f"Log file:           {log_file}")
    print()

    iteration = 0

    while True:
        # Check max iterations
        if max_iterations > 0 and iteration >= max_iterations:
            print(f"Max iterations ({max_iterations}) reached.")
            if logger:
                logger.log_event("max_iterations_reached", {"max_iterations": max_iterations})
            break

        iteration += 1

        print("--------------------------------------")
        print(f"  Iteration {iteration} of {max_iterations}")
        print("--------------------------------------")

        # Log iteration start
        if logger:
            logger.log_iteration_start(iteration, pending_tasks=None)

        # Check if all tasks are complete
        if spec_format == "json":
            pending = check_json_completion(spec_file)
        else:
            pending = check_markdown_completion(spec_file)

        if pending == 0:
            print("All stories complete! Exiting loop.")
            if logger:
                logger.log_event("all_tasks_complete", {"iteration": iteration})
            break

        print(f"Pending stories: {pending}")
        print()

        # Update pending count in iteration start log
        if logger:
            logger.log_event("pending_count", {"iteration": iteration, "pending": pending})

        # Log iteration start to progress file
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(progress_file, "a") as f:
            f.write(f"\n### Iteration {iteration} - {timestamp}\n")

        # Generate format-specific prompt
        if spec_format == "json":
            prompt = generate_json_prompt(spec_basename, progress_file, completion_promise)
        else:
            prompt = generate_markdown_prompt(spec_basename, progress_file, completion_promise)

        # Run Claude iteration with model and logger
        print("Running Claude...")
        iteration_start = time.time()
        try:
            exit_code, output = run_claude_iteration(prompt, progress_file, iteration, model, logger)
            iteration_duration = time.time() - iteration_start

            if exit_code == 0:
                print("Iteration completed successfully")
                with open(progress_file, "a") as f:
                    f.write("Status: Completed\n")

                # Log iteration end
                if logger:
                    logger.log_iteration_end(iteration, success=True, duration=iteration_duration)

                # Check for completion promise
                if check_completion_promise(output, completion_promise):
                    print()
                    print(f"Completion promise detected: '{completion_promise}'")
                    if logger:
                        logger.log_event("completion_promise_detected",
                                       {"iteration": iteration, "promise": completion_promise})
                    break
            else:
                print("Iteration failed")
                with open(progress_file, "a") as f:
                    f.write("Status: Failed\n")

                # Log iteration failure
                if logger:
                    logger.log_iteration_end(iteration, success=False, duration=iteration_duration,
                                           exit_code=exit_code)
        except Exception as e:
            iteration_duration = time.time() - iteration_start
            print(f"Exception during iteration: {e}")
            with open(progress_file, "a") as f:
                f.write(f"Status: Exception - {e}\n")

            # Log exception
            if logger:
                logger.log_error("iteration_exception", str(e), iteration=iteration,
                               duration=iteration_duration)
            raise

        # Commit any changes
        commit_changes(spec_name, iteration)

        # Sleep between iterations
        time.sleep(2)

    # Final status
    print()
    print("======================================")
    print("  Ralph Loop Complete")
    print("======================================")

    if spec_format == "json":
        final_pending = check_json_completion(spec_file)
    else:
        final_pending = check_markdown_completion(spec_file)

    # Close logger
    if logger:
        logger.log_event("ralph_loop_complete", {
            "total_iterations": iteration,
            "final_pending": final_pending,
            "success": final_pending == 0
        })
        logger.close()

    if final_pending == 0:
        print("SUCCESS: All stories completed!")
        return 0
    else:
        print(f"INCOMPLETE: {final_pending} stories remaining")
        return 1


def main() -> int:
    """Main entry point for ralph-loop."""
    args = parse_arguments()
    return run_ralph_loop(args)


if __name__ == "__main__":
    sys.exit(main())
