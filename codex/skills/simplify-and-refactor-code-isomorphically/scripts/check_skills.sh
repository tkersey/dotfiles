#!/usr/bin/env bash
# check_skills.sh — detect installed sibling skills + jsm state.
# Pattern adapted from documentation-website-for-software-project.
#
# Usage: check_skills.sh [workspace-dir]
# Writes: <workspace>/skill_inventory.json
# Exits 0 even when skills/jsm missing.

set -euo pipefail

WORKSPACE="${1:-refactor/artifacts/$(date +%Y-%m-%d)-pass-1}"
mkdir -p "$WORKSPACE"
OUT="$WORKSPACE/skill_inventory.json"

# Siblings this skill references (grouped by phase in JSM-BOOTSTRAP.md)
REFERENCED_SKILLS=(
  cass
  codebase-archaeology
  mock-code-finder
  ubs
  multi-pass-bug-hunting
  testing-golden-artifacts
  testing-metamorphic
  testing-fuzzing
  testing-real-service-e2e-no-mocks
  e2e-testing-for-webapps
  multi-model-triangulation
  code-review-gemini-swarm-with-ntm
  cc-hooks
  agent-mail
  ntm
  vibing-with-ntm
  br
  beads-workflow
  bv
  caam
  profiling-software-performance
  extreme-software-optimization
  deadlock-finder-and-fixer
  readme-writing
  de-slopify
  porting-to-rust
  supabase
  vercel
  tanstack
  planning-workflow
  multi-agent-swarm-workflow
  dcg
  frankensearch-integration-for-rust-projects
)

SKILL_SEARCH_PATHS=(
  "${CLAUDE_SKILLS_PATH:-}"
  "$HOME/.claude/skills"
  ".claude/skills"
)

JSM_AVAILABLE=false; JSM_VERSION=""
if command -v jsm >/dev/null 2>&1; then
  JSM_AVAILABLE=true
  JSM_VERSION="$(jsm --version 2>&1 | head -1 || echo 'unknown')"
fi

JSM_AUTHED=false
SUBSCRIPTION_TIER="unknown"
if [[ "$JSM_AVAILABLE" == "true" ]]; then
  if whoami_out=$(jsm whoami 2>&1) && ! echo "$whoami_out" | grep -qi 'not logged in'; then
    JSM_AUTHED=true
    if tier=$(jsm whoami --json 2>/dev/null | grep -oE '"status"[^,}]*' | head -1 | sed 's/.*"\([^"]*\)".*/\1/'); then
      [[ -n "$tier" ]] && SUBSCRIPTION_TIER="$tier"
    fi
  fi
fi

find_skill() {
  local name="$1"
  for base in "${SKILL_SEARCH_PATHS[@]}"; do
    [[ -z "$base" ]] && continue
    if [[ -f "$base/$name/SKILL.md" ]]; then
      echo "$base/$name"; return 0
    fi
  done
  return 1
}

# Emit JSON
{
  printf '{\n'
  printf '  "checked_at": "%s",\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf '  "jsm_available": %s,\n' "$JSM_AVAILABLE"
  printf '  "jsm_version": "%s",\n' "$JSM_VERSION"
  printf '  "jsm_authenticated": %s,\n' "$JSM_AUTHED"
  printf '  "subscription_tier": "%s",\n' "$SUBSCRIPTION_TIER"
  printf '  "skills": [\n'
  total=${#REFERENCED_SKILLS[@]}
  for idx in "${!REFERENCED_SKILLS[@]}"; do
    name="${REFERENCED_SKILLS[$idx]}"
    if path=$(find_skill "$name"); then
      status="present"
    else
      status="missing"; path=""
    fi
    printf '    {"name": "%s", "status": "%s", "path": "%s"}' "$name" "$status" "$path"
    if (( idx < total - 1 )); then printf ','; fi
    printf '\n'
  done
  printf '  ]\n}\n'
} > "$OUT"

# Human-readable table
printf '\n=== Sibling skill inventory ===\n'
printf '%-42s  %-8s  %s\n' 'skill' 'status' 'location'
printf '%-42s  %-8s  %s\n' '------------------------------------------' '--------' '------------------------------------------'
for name in "${REFERENCED_SKILLS[@]}"; do
  if path=$(find_skill "$name"); then
    printf '%-42s  \033[32m%-8s\033[0m  %s\n' "$name" 'present' "$path"
  else
    printf '%-42s  \033[33m%-8s\033[0m  %s\n' "$name" 'missing' '(use jsm install or inline fallback)'
  fi
done

printf '\n'
if [[ "$JSM_AVAILABLE" == "true" ]]; then
  printf 'jsm: installed (%s); authenticated=%s; subscription=%s\n' \
    "$JSM_VERSION" "$JSM_AUTHED" "$SUBSCRIPTION_TIER"
else
  printf 'jsm: not installed. Run ./scripts/install_jsm.sh to install.\n'
fi

printf '\nwrote %s\n' "$OUT"
