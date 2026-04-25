#!/usr/bin/env bash
# install_missing_skills.sh — bulk jsm install for missing siblings.
# Reads skill_inventory.json written by check_skills.sh.
# Exits 0 even on failures; logs to missing_skills.md.
#
# Usage: install_missing_skills.sh [workspace-dir]

set -euo pipefail

WORKSPACE="${1:-refactor/artifacts/$(date +%Y-%m-%d)-pass-1}"
INV="$WORKSPACE/skill_inventory.json"
LOG="$WORKSPACE/missing_skills.md"

if [[ ! -f "$INV" ]]; then
  echo "error: $INV not found. Run ./scripts/check_skills.sh first." >&2
  exit 2
fi

if ! command -v jsm >/dev/null 2>&1; then
  echo "jsm not installed. All missing siblings will use inline fallbacks."
  echo "  To install jsm: ./scripts/install_jsm.sh"
  exit 0
fi

# Check auth
if ! whoami_out=$(jsm whoami 2>&1) || echo "$whoami_out" | grep -qi 'not logged in'; then
  cat <<EOF
jsm is installed but not authenticated. Run:

  jsm login

Or for headless environments:
  jsm auth                                # API key prompt
  jsm login --print-url                   # copy URL, open on your laptop

Continuing with inline fallbacks for missing siblings.
EOF
  exit 0
fi

# Extract missing skill names (avoids jq dep)
missing=$(grep -oE '"name": "[^"]+", "status": "missing"' "$INV" \
  | sed -E 's/.*"name": "([^"]+)".*/\1/' || true)

if [[ -z "$missing" ]]; then
  echo "All referenced sibling skills are already installed. Nothing to do."
  exit 0
fi

: > "$LOG"
{
  echo "# Missing sibling skills — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  echo "Attempting \`jsm install\` for each:"
  echo
} >> "$LOG"

installed=0
skipped=0
for skill in $missing; do
  printf 'installing %s ... ' "$skill"
  if out=$(jsm install "$skill" 2>&1); then
    echo "ok"
    installed=$((installed+1))
    echo "- \`$skill\` — **installed via jsm**" >> "$LOG"
  else
    if   echo "$out" | grep -qi 'subscription'; then
      reason='subscription required (paid jeffreys-skills.md account)'
    elif echo "$out" | grep -qi 'not found\|404';  then
      reason='skill not in jsm catalog; inline fallback applies'
    elif echo "$out" | grep -qi 'network\|timeout\|unreachable'; then
      reason='network error; retry later'
    else
      reason="$(echo "$out" | head -2 | tr '\n' ' ')"
    fi
    echo "skip ($reason)"
    skipped=$((skipped+1))
    printf -- "- \`%s\` — **not installed**: %s\n  - fallback: use inline prompts from this skill's references/\n" "$skill" "$reason" >> "$LOG"
  fi
done

{
  echo
  echo "## Summary"
  echo
  echo "- installed: $installed"
  echo "- skipped:   $skipped"
  echo
  if (( skipped > 0 )); then
    cat <<EOF
Skipped siblings use inline fallbacks. This skill is designed to run end-to-end
without any sibling; the siblings are accelerants, not prerequisites.

To unlock premium siblings, subscribe at https://jeffreys-skills.md (\$20/mo),
run \`jsm login\`, and re-run this script.
EOF
  fi
} >> "$LOG"

echo
echo "logged to $LOG"
echo "installed=$installed  skipped=$skipped"
