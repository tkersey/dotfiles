#!/usr/bin/env bash
# scripts/validate_pass.sh — Pre-flight + end checklist enforcement.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/validate_pass.sh <sibling-dir>

Validates that an audit workspace (the sibling directory) is internally
consistent. Checks: manifest is valid JSON; every applied:true rec has a
matching applied_changes row + regression test; every applied:false rec in a
completed full pass has a deferred_reason; every score > 700 has evidence;
HANDOFF.md exists for completed passes.

Args:
  <sibling-dir>   Absolute path to the audit workspace (the
                  <target>__agent_ergonomics_audit/ sibling directory).

Output:
  Violation messages to stderr; one summary line to stdout on success.

Exit codes:
  0  Pass is consistent.
  1  One or more checks failed (count printed to stderr).
  2  Missing arguments, or sibling directory does not exist (input error,
     distinct from the "checks failed" case so a CI runner can tell them
     apart).

Example:
  scripts/validate_pass.sh /path/to/mytool__agent_ergonomics_audit
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 2 ;;
esac

SIBLING="$1"
AUDIT="$SIBLING/audit"

if [ ! -d "$AUDIT" ]; then
  echo "audit directory not found: $AUDIT" >&2
  exit 2
fi

violations=0
fail() {
  echo "VIOLATION: $1" >&2
  violations=$((violations + 1))
}

# 1. manifest.json exists and is valid
if [ ! -f "$AUDIT/manifest.json" ]; then
  fail "manifest.json missing"
else
  jq . "$AUDIT/manifest.json" >/dev/null 2>&1 || fail "manifest.json invalid JSON"
fi

# 2. Every applied:true rec has a corresponding applied_changes.jsonl row
if [ -f "$AUDIT/recommendations.jsonl" ] && [ -f "$AUDIT/applied_changes.jsonl" ]; then
  applied_rids=$(jq -r 'select(.recommendation_id) | .recommendation_id' "$AUDIT/applied_changes.jsonl" 2>/dev/null | sort -u)
  while IFS= read -r rec; do
    rid=$(echo "$rec" | jq -r '.recommendation_id // empty')
    applied=$(echo "$rec" | jq -r '.applied // false')
    [ -z "$rid" ] && continue
    if [ "$applied" = "true" ] && ! echo "$applied_rids" | grep -qx "$rid"; then
      fail "rec $rid is applied:true but no applied_changes entry"
    fi
  done < "$AUDIT/recommendations.jsonl"
fi

# 3. Every applied:true rec has a regression test
if [ -f "$AUDIT/recommendations.jsonl" ] && [ -d "$AUDIT/regression_tests" ]; then
  while IFS= read -r rec; do
    rid=$(echo "$rec" | jq -r '.recommendation_id // empty')
    applied=$(echo "$rec" | jq -r '.applied // false')
    [ -z "$rid" ] && continue
    if [ "$applied" = "true" ]; then
      if ! ls "$AUDIT/regression_tests/${rid}__"*.test.* >/dev/null 2>&1; then
        fail "rec $rid is applied:true but no regression test in regression_tests/${rid}__*.test.*"
      fi
    fi
  done < "$AUDIT/recommendations.jsonl"
fi

# 4. Every applied:false rec has a deferred_reason — but only at end of `full` pass.
#    During audit-only mode, all recs are applied:false with null deferred_reason; that's expected.
#    We use the pass's `mode` field + `completed_at` to determine if the check should fire.
if [ -f "$AUDIT/recommendations.jsonl" ] && [ -f "$AUDIT/manifest.json" ]; then
  pass_mode=$(jq -r '.passes[-1].mode // empty' "$AUDIT/manifest.json" 2>/dev/null)
  pass_completed=$(jq -r '.passes[-1].completed_at // empty' "$AUDIT/manifest.json" 2>/dev/null)
  if [ "$pass_mode" = "full" ] && [ -n "$pass_completed" ]; then
    while IFS= read -r rec; do
      rid=$(echo "$rec" | jq -r '.recommendation_id // empty')
      applied=$(echo "$rec" | jq -r '.applied // false')
      deferred=$(echo "$rec" | jq -r '.deferred_reason // ""')
      [ -z "$rid" ] && continue
      if [ "$applied" = "false" ] && [ -z "$deferred" ]; then
        fail "rec $rid is applied:false but has empty deferred_reason (full pass complete)"
      fi
    done < "$AUDIT/recommendations.jsonl"
  fi
fi

# 5. No score > 700 lacks evidence
if [ -f "$AUDIT/agent_surfaces.jsonl" ]; then
  while IFS= read -r row; do
    sid=$(echo "$row" | jq -r '.surface_id')
    for dim in agent_intuitiveness agent_ergonomics agent_ease_of_use output_parseability error_pedagogy intent_inference safety_with_recovery determinism_and_reproducibility self_documentation composability regression_resistance; do
      score=$(echo "$row" | jq -r ".scores.\"$dim\" // \"\"")
      [ -z "$score" ] && continue
      [ "$score" = "null" ] && continue
      # Defensive: ensure score is integer
      [[ "$score" =~ ^[0-9]+$ ]] || continue
      if [ "$score" -gt 700 ]; then
        ev=$(echo "$row" | jq ".evidence.\"$dim\" // null")
        if [ "$ev" = "null" ]; then
          notes=$(echo "$row" | jq -r '.notes // ""')
          if ! echo "$notes" | grep -qiE 'n/a'; then
            fail "surface $sid has score $score on $dim but no evidence"
          fi
        fi
      fi
    done
  done < "$AUDIT/agent_surfaces.jsonl"
fi

# 6. HANDOFF.md exists for completed passes
if [ -f "$AUDIT/manifest.json" ]; then
  current=$(jq -r '.current_pass // 1' "$AUDIT/manifest.json")
  if [ ! -f "$AUDIT/HANDOFF.md" ] && [ -f "$AUDIT/applied_changes.jsonl" ]; then
    fail "applied_changes.jsonl exists but HANDOFF.md missing for pass $current"
  fi
fi

# 7. No file deletions in target between passes (best-effort detection)
# (full check requires git context; skipped here)

if [ "$violations" -gt 0 ]; then
  echo
  echo "$violations violation(s) detected." >&2
  exit 1
fi

echo "validate_pass: OK ($AUDIT)"
exit 0
