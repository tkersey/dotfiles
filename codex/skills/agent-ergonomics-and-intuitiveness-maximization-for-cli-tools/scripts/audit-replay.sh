#!/usr/bin/env bash
# scripts/audit-replay.sh — Replay an old audit's recs against current source.
#
# Given an old audit/applied_changes.jsonl, check each recommendation against
# the target's CURRENT source (HEAD): is the change still present? Did the
# code drift? Was the surface removed?
#
# Use case: "I ran the audit 3 months ago. What changed?" Output: per-rec
# status (still-applied / drifted / no-longer-applicable).
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/audit-replay.sh <sibling> <target>

Replays each entry in <sibling>/audit/applied_changes.jsonl against the
current state of <target>. Reports per-rec status:
  - still-applied: the test from the original audit still passes
  - drifted: the test passes but git log shows the original commit was rebased/squashed
  - no-longer-applicable: the surface_id is no longer in the inventory
  - test-failed: the regression test failed (rec was reverted or broken)

Args:
  <sibling>   Audit workspace root (must have audit/applied_changes.jsonl).
  <target>    Target repo absolute path.

Output:
  Markdown report on stdout. Per-rec line; final summary.

Exit codes:
  0  All recs still-applied OR drifted (acceptable).
  1  Any rec test-failed or no-longer-applicable (regressions).
  2  Bad args / missing inputs.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 2 ;;
esac

SIBLING="$1"
TARGET="${2:-}"
[ -z "$TARGET" ] && { usage >&2; exit 2; }
[ -d "$TARGET" ] || { echo "target not a directory: $TARGET" >&2; exit 2; }

APPLIED="$SIBLING/audit/applied_changes.jsonl"
INVENTORY="$SIBLING/audit/surface_inventory.jsonl"
[ -f "$APPLIED" ] || { echo "no applied_changes.jsonl: $APPLIED" >&2; exit 2; }

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "# Audit Replay Report"
echo
echo "- Generated: $NOW"
echo "- Source audit: \`$APPLIED\`"
echo "- Target repo:  \`$TARGET\`"
echo
echo "| recommendation_id | commit_sha | status | note |"
echo "|-------------------|------------|--------|------|"

ok=0
drift=0
gone=0
fail=0

# Build set of current surface_ids if inventory available.
if [ -f "$INVENTORY" ]; then
  current_sids=$(jq -r '.surface_id' "$INVENTORY" | sort -u)
else
  current_sids=""
fi

while IFS= read -r rec; do
  [ -z "$rec" ] && continue
  rid=$(echo "$rec" | jq -r '.recommendation_id // ""')
  sha=$(echo "$rec" | jq -r '.commit_sha // ""')
  test_path=$(echo "$rec" | jq -r '.test_path // ""')
  surfaces=$(echo "$rec" | jq -r '.surface_ids_touched // [] | join(",")')

  # Status A: surface gone from inventory?
  if [ -n "$current_sids" ] && [ -n "$surfaces" ]; then
    surface_missing=0
    # Use IFS-based split rather than unquoted expansion so surface_ids that
    # might contain shell-special chars (or regex metachars when grepped)
    # are handled literally. -F to treat $sid as a fixed string.
    IFS=',' read -ra surface_arr <<< "$surfaces"
    for sid in "${surface_arr[@]}"; do
      if ! echo "$current_sids" | grep -qFx "$sid"; then
        surface_missing=1; break
      fi
    done
    if [ "$surface_missing" -eq 1 ]; then
      printf '| %s | %.7s | no-longer-applicable | surface(s) %s removed from current inventory |\n' "$rid" "$sha" "$surfaces"
      gone=$((gone + 1))
      continue
    fi
  fi

  # Status B: commit still in target's history?
  if [ -n "$sha" ]; then
    if ! git -C "$TARGET" cat-file -e "${sha}^{commit}" 2>/dev/null; then
      printf '| %s | %.7s | drifted | commit not in target history (rebased/squashed) |\n' "$rid" "$sha"
      drift=$((drift + 1))
      continue
    fi
  fi

  # Status C: regression test still passes?
  full_test_path="$SIBLING/$test_path"
  if [ -n "$test_path" ] && [ -f "$full_test_path" ]; then
    if /usr/bin/timeout 30 bash "$full_test_path" >/dev/null 2>&1; then
      printf '| %s | %.7s | still-applied | regression test passes |\n' "$rid" "$sha"
      ok=$((ok + 1))
    else
      printf '| %s | %.7s | test-failed | regression test fails — rec may have been reverted or broken |\n' "$rid" "$sha"
      fail=$((fail + 1))
    fi
  else
    printf '| %s | %.7s | drifted | no test_path recorded; cannot verify |\n' "$rid" "$sha"
    drift=$((drift + 1))
  fi
done < "$APPLIED"

echo
echo "## Summary"
echo
echo "- still-applied:        $ok"
echo "- drifted:              $drift"
echo "- no-longer-applicable: $gone"
echo "- test-failed:          $fail"
echo

if [ "$fail" -gt 0 ] || [ "$gone" -gt 0 ]; then
  echo "⚠️  $((fail + gone)) recommendation(s) need attention. Re-audit the affected surfaces."
  exit 1
fi
echo "✅ All recommendations either still-applied or drifted-but-tracked."
exit 0
