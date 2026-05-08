#!/usr/bin/env bash
# scripts/check-skills.sh — Inventory referenced helper skills + jsm state.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/check-skills.sh <audit-dir>

Phase 0.5: detects which helper skills referenced by this skill are present
on this system, and whether `jsm` is installed. Writes the inventory as
phase0_skill_inventory.json into <audit-dir> and prints a one-line summary
to stdout. Exits 0 even if some skills are missing (advisory).

Args:
  <audit-dir>   Absolute path to the audit/ directory inside the sibling
                workspace. Created with mkdir -p if it does not exist.

Output:
  Writes <audit-dir>/phase0_skill_inventory.json. Summary on stdout.

Example:
  scripts/check-skills.sh /path/to/mytool__agent_ergonomics_audit/audit

Exit codes:
  0  Always (advisory).
  1  Missing arguments (usage printed). Refuses to default to ./audit so
     calling this from the wrong cwd doesn't side-effect into a surprise
     directory.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

AUDIT_DIR="$1"
mkdir -p "$AUDIT_DIR"

REQUIRED_SKILLS=(
  sc sw operationalizing-expertise codebase-archaeology codebase-report
  multi-pass-bug-hunting multi-model-triangulation ubs dcg agent-mail br bv cass
  idea-wizard github cc-hooks
)

JSM_PRESENT=false
if command -v jsm >/dev/null 2>&1; then
  JSM_PRESENT=true
fi

# Try to detect installed skills from the known Claude/Codex roots plus the
# repo-local sibling skill directory that contains this skill.
PROJECT_SKILL_INDEX="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CLAUDE_SKILL_INDEX="${HOME}/.claude/skills"
CODEX_SKILL_INDEX="${CODEX_HOME:-$HOME/.codex}/skills"
detect_skill() {
  local name="$1"
  local root
  for root in "$CLAUDE_SKILL_INDEX" "$CODEX_SKILL_INDEX" "$PROJECT_SKILL_INDEX"; do
    if [ -d "$root/$name" ]; then
      echo "true"
      return
    fi
  done
  echo "false"
}

# Build inventory JSON
{
  echo '{'
  echo '  "checked_at": "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'",'
  echo '  "jsm_present": '"$JSM_PRESENT"','
  echo '  "skills": {'
  first=true
  for skill in "${REQUIRED_SKILLS[@]}"; do
    present=$(detect_skill "$skill")
    [ "$first" = true ] || echo ','
    first=false
    printf '    "%s": {"present": %s}' "$skill" "$present"
  done
  echo
  echo '  }'
  echo '}'
} > "$AUDIT_DIR/phase0_skill_inventory.json"

# Print summary to stdout
echo "skill inventory written to: $AUDIT_DIR/phase0_skill_inventory.json"
missing=$(grep -c '"present": false' "$AUDIT_DIR/phase0_skill_inventory.json" || true)
echo "skills missing: $missing / ${#REQUIRED_SKILLS[@]}"
echo "jsm present: $JSM_PRESENT"

exit 0
