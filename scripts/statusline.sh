#!/bin/bash
#
# Claude Code Status Line
#
# Requirements: jq (for JSON parsing)
# Install: brew install jq (macOS) or apt-get install jq (Linux)

# Check for required dependencies
if ! command -v jq &>/dev/null; then
  echo "[install jq: brew install jq]"
  exit 0
fi

# Read JSON input from Claude Code
input=$(cat)

# Consolidate JSON parsing into single jq call using TSV output
# If jq fails (invalid JSON), set safe defaults
if ! IFS=$'\t' read -r model current_dir tokens context_limit < <(echo "$input" | jq -r '[
    (.model.display_name // "Unknown"),
    (.workspace.current_dir // "~"),
    (.context_window.total_input_tokens + .context_window.total_output_tokens),
    (.context_window.context_window // 200000)
] | @tsv' 2>/dev/null); then
  # JSON parsing failed, use safe defaults
  echo "[statusline: invalid JSON input]"
  exit 0
fi

dir_name=$(basename "$current_dir")

# Validate numeric values
[[ ! "$tokens" =~ ^[0-9]+$ ]] && tokens=0
[[ ! "$context_limit" =~ ^[0-9]+$ ]] && context_limit=200000

# Calculate remaining percentage
if [ "$context_limit" -gt 0 ]; then
  remaining_pct=$(( 100 - (tokens * 100 / context_limit) ))
  [ "$remaining_pct" -lt 0 ] && remaining_pct=0
else
  remaining_pct=100
fi

# Format tokens in compact form (e.g., 49k, 200k)
format_compact() {
  local num=$1
  if [ "$num" -ge 1000000 ]; then
    printf "%.1fM" "$(echo "scale=1; $num / 1000000" | bc)"
  elif [ "$num" -ge 1000 ]; then
    printf "%.0fk" "$(echo "scale=0; $num / 1000" | bc)"
  else
    printf "%d" "$num"
  fi
}

tokens_compact=$(format_compact "$tokens")
limit_compact=$(format_compact "$context_limit")

# ANSI color codes using $'...' so escapes are interpreted at assignment time
# This allows us to use printf '%s' safely later (no interpretation of branch names)
RED=$'\033[91m'
YELLOW=$'\033[93m'
GREEN=$'\033[92m'
GREY=$'\033[90m'
RESET=$'\033[0m'

# Cache configuration - use consistent hash of directory
CACHE_FILE="/tmp/claude-statusline-cache-${USER}-$(echo -n "$current_dir" | md5 -q)"
CACHE_DURATION=3 # seconds

# Function to get git info (expensive operations)
get_git_info() {
  local git_info=""
  local color="$RESET"

  # Check if we're in a git repository
  if git rev-parse --git-dir >/dev/null 2>&1; then
    # Get repository name
    local repo_name=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)")

    # Get current branch
    local branch=$(git branch --show-current 2>/dev/null)
    [ -z "$branch" ] && branch="detached"

    # Use single git status call instead of multiple git diff calls
    local staged_count=0
    local unstaged_count=0
    local untracked_count=0

    while IFS= read -r line; do
      local index_status="${line:0:1}"
      local work_status="${line:1:1}"

      # Count untracked files (both status chars are ?)
      if [[ "$index_status" == "?" && "$work_status" == "?" ]]; then
        ((untracked_count++))
      else
        # Count staged files (index status is not space or ?)
        [[ "$index_status" != " " && "$index_status" != "?" ]] && ((staged_count++))

        # Count unstaged files (work status is not space or ?)
        [[ "$work_status" != " " && "$work_status" != "?" ]] && ((unstaged_count++))
      fi
    done < <(git status --porcelain=v1 2>/dev/null)

    # Check if there are unpushed commits and upstream status
    local unpushed_count=0
    local no_upstream=false
    local upstream=$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null)
    if [ -n "$upstream" ] && [ "$upstream" != "@{u}" ]; then
      unpushed_count=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo "0")
    else
      # No upstream tracking branch
      no_upstream=true
    fi

    # Determine color based on git status
    if [ "$unstaged_count" -gt 0 ]; then
      color="$RED" # Red if unstaged changes
    elif [ "$staged_count" -gt 0 ] || [ "$unpushed_count" -gt 0 ] || [ "$untracked_count" -gt 0 ] || [ "$no_upstream" = true ]; then
      color="$YELLOW" # Yellow if staged, unpushed, untracked, or no upstream
    else
      color="$GREEN" # Green if clean
    fi

    # Build git status indicators (avoid leading spaces)
    local status_indicators=""
    [ "$staged_count" -gt 0 ] && status_indicators="+${staged_count}"
    [ "$unstaged_count" -gt 0 ] && status_indicators="${status_indicators:+$status_indicators }!${unstaged_count}"
    [ "$untracked_count" -gt 0 ] && status_indicators="${status_indicators:+$status_indicators }?${untracked_count}"
    [ "$unpushed_count" -gt 0 ] && status_indicators="${status_indicators:+$status_indicators }↑${unpushed_count}"
    [ "$no_upstream" = true ] && status_indicators="${status_indicators:+$status_indicators }⚠"

    # Format git info with color
    git_info="${color}${repo_name}:${branch}${status_indicators:+ [$status_indicators]}${RESET}"
  else
    # Not in a git repo, just show directory in grey
    color="$GREY"
    git_info="${color}${dir_name}${RESET}"
  fi

  # Save to cache with timestamp
  # Use base64 to safely encode git_info (handles any special characters)
  # Strip newlines to prevent line wrapping issues
  local git_info_b64=$(echo -n "$git_info" | base64 | tr -d '\n')
  echo "$(date +%s) $git_info_b64" >"$CACHE_FILE"
  echo "$git_info"
}

# Try to use cached git info
git_info=""
if [ -f "$CACHE_FILE" ]; then
  cache_line=$(cat "$CACHE_FILE" 2>/dev/null)
  cache_time=$(echo "$cache_line" | cut -d' ' -f1)
  cached_git_info_b64=$(echo "$cache_line" | cut -d' ' -f2-)

  # Validate cache_time is numeric
  if [[ "$cache_time" =~ ^[0-9]+$ ]]; then
    current_time=$(date +%s)
    age=$((current_time - cache_time))

    if [ "$age" -lt "$CACHE_DURATION" ]; then
      # Cache is fresh, decode and use it (try macOS -D first, then Linux -d)
      git_info=$(echo "$cached_git_info_b64" | base64 -D 2>/dev/null || echo "$cached_git_info_b64" | base64 -d 2>/dev/null || echo "")
    fi
  fi

  # If cache was invalid or stale, refresh it
  [ -z "$git_info" ] && git_info=$(get_git_info)
else
  # No cache exists, create it
  git_info=$(get_git_info)
fi

# Output the status line using printf '%s\n' since colors are already interpreted
printf '%s\n' "[$model] $git_info | ${tokens_compact}/${limit_compact} tokens (${remaining_pct}% remaining)"
