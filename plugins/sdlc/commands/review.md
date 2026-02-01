# Run Automated Code Review Loop

Run an iterative automated code review loop on current code changes. The review loop continuously runs ACR (Automated Code Review), diagnoses findings as real issues or false positives, and takes appropriate action (fix real issues, add comments for false positives) until ACR returns only false positives or exits successfully (LGTM).

## Instructions

- Parse the arguments from `$ARGUMENTS` to extract review configuration options
- Invoke the review-loop script: `plugins/sdlc/scripts/review-loop` with the parsed arguments
- The script accepts the following options:
  - `--max-iterations`, `-m`: Maximum review/fix cycles (default: 5)
  - `--num-reviewers`, `-r`: Number of ACR reviewers (default: 5)
  - `--model`: Model to use for triage (default: "claude")
  - `--verbose`, `-v`: Enable verbose logging
  - `--log`, `--log-file`: Path to log file for detailed execution capture
- Display the script output to the user
- If the script exits with an error, report the error clearly

## Arguments

$ARGUMENTS

## Usage Examples

Basic usage (use all defaults):
```
/sdlc:review
```

With custom max iterations:
```
/sdlc:review --max-iterations 3
```

With verbose output and custom reviewers:
```
/sdlc:review -v -r 10
```

Full configuration:
```
/sdlc:review --max-iterations 5 --num-reviewers 10 --model claude --verbose --log .my-review.log
```

## How It Works

1. The review-loop script runs ACR with flags: `--local -a claude -s claude -r N` (where N is num-reviewers)
2. ACR analyzes code changes and reports findings
3. If ACR returns exit code 0 (LGTM), the loop exits successfully
4. If ACR returns exit code 1 (findings), the script:
   - Displays a structured summary of findings
   - Invokes Claude to diagnose each finding (real issue vs false positive)
   - Fixes real issues with minimal code changes
   - Adds explanatory comments for false positives
   - Repeats the review cycle
5. The loop continues until LGTM or max iterations reached
6. All summaries are logged to `.review-loop.log` (or custom log file)

## Configuration

The review-loop script supports configuration via `.claude-kit` files in the following precedence order:
- Home directory: `~/.claude-kit`
- Git root directory: `<git-root>/.claude-kit`
- Current working directory: `./.claude-kit`
- Command-line arguments (highest priority)

Example `.claude-kit` configuration:
```json
{
  "review_loop": {
    "max_iterations": 5,
    "model": "claude",
    "verbose": false
  },
  "acr": {
    "num_reviewers": 5,
    "analyzer_model": "claude",
    "summarizer_model": "claude"
  }
}
```

## Report

After the review loop completes:
- Summarize the review results (number of iterations, findings fixed, false positives identified)
- Report final status (LGTM, max iterations reached, or error)
- Note the log file location for detailed review history
