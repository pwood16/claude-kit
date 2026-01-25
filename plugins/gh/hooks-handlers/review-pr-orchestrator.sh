#!/bin/bash
set -e

work_dir="$1"
repo_path="$2"  # Path to review (worktree path if using worktree)
worktree_path="${3:-}"  # Optional: worktree path to clean up when done
original_repo="${4:-}"  # Optional: original repo for worktree cleanup

# Per-agent timeout (5 minutes)
AGENT_TIMEOUT=300

# Cleanup function for worktree
cleanup_worktree() {
  if [ -n "$worktree_path" ] && [ -d "$worktree_path" ] && [ -n "$original_repo" ]; then
    echo "Cleaning up worktree: $worktree_path"
    cd "$original_repo" 2>/dev/null || true
    git worktree remove "$worktree_path" --force 2>/dev/null || true
  fi
}

# Ensure cleanup runs on exit (success or failure)
trap cleanup_worktree EXIT

# Portable timeout function (works on macOS and Linux)
run_with_timeout() {
  local timeout_seconds="$1"
  shift

  # Try GNU timeout first (Linux), then gtimeout (macOS with coreutils)
  if command -v timeout >/dev/null 2>&1; then
    timeout "$timeout_seconds" "$@"
  elif command -v gtimeout >/dev/null 2>&1; then
    gtimeout "$timeout_seconds" "$@"
  else
    # Fallback: run without timeout but with manual watchdog
    local cmd_pid
    "$@" &
    cmd_pid=$!

    # Watchdog in background
    (
      sleep "$timeout_seconds"
      kill -TERM "$cmd_pid" 2>/dev/null
    ) &
    local watchdog_pid=$!

    # Wait for command
    if wait "$cmd_pid" 2>/dev/null; then
      kill "$watchdog_pid" 2>/dev/null
      return 0
    else
      local exit_code=$?
      kill "$watchdog_pid" 2>/dev/null
      return $exit_code
    fi
  fi
}

# Status tracking (5 steps total: arch, quality x3, finalizer)
update_status() {
  local status="$1"
  local step="$2"
  local error="${3:-null}"
  cat > "$work_dir/status.json" <<EOF
{
  "status": "$status",
  "current_step": $step,
  "total_steps": 5,
  "step_names": ["architecture", "quality-pass1", "quality-pass2", "quality-final", "summary"],
  "updated_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "error": $error
}
EOF
}

# Run agent with timeout and error handling
run_agent() {
  local agent_name="$1"
  local output_file="$2"
  local prompt="$3"
  shift 3
  local input_files=("$@")

  local output
  local tmp_output
  tmp_output=$(mktemp)

  # Concatenate input files with markers for agent parsing
  local combined_input
  combined_input=$(mktemp)
  for file in "${input_files[@]}"; do
    echo "=== FILE: $(basename "$file") ===" >> "$combined_input"
    cat "$file" >> "$combined_input"
    echo "" >> "$combined_input"
  done

  if cat "$combined_input" | run_with_timeout $AGENT_TIMEOUT claude --print \
    --agent "$agent_name" \
    --max-turns 50 \
    "$prompt" > "$tmp_output" 2>&1; then
    rm -f "$combined_input"
    mv "$tmp_output" "$output_file"
    return 0
  else
    local exit_code=$?
    rm -f "$combined_input"
    if [ $exit_code -eq 124 ] || [ $exit_code -eq 143 ]; then
      echo "Agent timed out after ${AGENT_TIMEOUT}s" > "$output_file.error"
      rm -f "$tmp_output"
      return 124
    else
      mv "$tmp_output" "$output_file.error"
      return $exit_code
    fi
  fi
}

# Check context size before starting
context_size=$(wc -c < "$work_dir/context.json")
MAX_CONTEXT_SIZE=$((500 * 1024))  # 500KB limit

if [ "$context_size" -gt "$MAX_CONTEXT_SIZE" ]; then
  update_status "failed" 0 '"PR too large for automated review. Context size: '"$context_size"' bytes exceeds limit of '"$MAX_CONTEXT_SIZE"' bytes. Consider breaking into smaller PRs."'
  exit 1
fi

# Agent 1: Architecture
update_status "in_progress" 1
if ! run_agent "gh:pr-architecture-reviewer" "$work_dir/1-architecture.md" \
  'Review this PR for architecture compliance:' \
  "$work_dir/context.json"; then
  update_status "failed" 1 '"Architecture review failed. Check 1-architecture.md.error for details."'
  exit 1
fi

# Agent 2: Quality Pass 1 - Initial review
update_status "in_progress" 2
if ! run_agent "gh:pr-quality-reviewer" "$work_dir/2-quality-pass1.md" \
  'Initial code quality review, building on architecture findings:' \
  "$work_dir/context.json" "$work_dir/1-architecture.md"; then
  update_status "failed" 2 '"Quality pass 1 failed. Check 2-quality-pass1.md.error for details."'
  exit 1
fi

# Agent 2: Quality Pass 2 - Refine with architecture context
update_status "in_progress" 3
if ! run_agent "gh:pr-quality-reviewer" "$work_dir/2-quality-pass2.md" \
  'Refine your quality review using architecture findings. Remove nitpicks, focus on what matters:' \
  "$work_dir/context.json" "$work_dir/1-architecture.md" "$work_dir/2-quality-pass1.md"; then
  update_status "failed" 3 '"Quality pass 2 failed. Check 2-quality-pass2.md.error for details."'
  exit 1
fi

# Agent 2: Quality Pass 3 - Synthesize
update_status "in_progress" 4
if ! run_agent "gh:pr-quality-reviewer" "$work_dir/2-quality-final.md" \
  'Synthesize the two quality passes into a final quality assessment:' \
  "$work_dir/context.json" "$work_dir/2-quality-pass1.md" "$work_dir/2-quality-pass2.md"; then
  update_status "failed" 4 '"Quality synthesis failed. Check 2-quality-final.md.error for details."'
  exit 1
fi

# Agent 3: Finalizer (includes all previous)
update_status "in_progress" 5
if ! run_agent "gh:pr-summary-finalizer" "$work_dir/3-final-summary.md" \
  'Create final summary with edge case analysis:' \
  "$work_dir/context.json" "$work_dir/1-architecture.md" "$work_dir/2-quality-final.md"; then
  update_status "failed" 5 '"Final summary failed. Check 3-final-summary.md.error for details."'
  exit 1
fi

update_status "completed" 5
