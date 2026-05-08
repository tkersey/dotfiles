#!/usr/bin/env bash
# tools/audit-compare.sh — Compare two audit workspaces.
#
# diff_scorecards.sh compares two PASSES within ONE workspace. This compares
# two SEPARATE workspaces (e.g. tool's main vs feature branch, or two tools
# at the same archetype rank). Per-surface and per-dim deltas; surfaces
# present in one but not the other; aggregate weighted_score change.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/audit-compare.sh <sibling-A> <sibling-B> [--pass-a N] [--pass-b N]

Compares the latest-pass agent_surfaces.jsonl from two audit workspaces.

Args:
  <sibling-A>     First audit workspace.
  <sibling-B>     Second audit workspace.
  --pass-a N      Filter A to specific pass (default: latest in A).
  --pass-b N      Filter B to specific pass (default: latest in B).

Output (markdown to stdout):
  - Header with both workspace paths
  - Surface-set comparison: in-both / only-in-A / only-in-B
  - Per-surface weighted_score delta table (B − A)
  - Per-dim aggregate delta (mean across surfaces)

Exit codes:
  0  Comparison produced.
  1  Bad args / missing workspace files.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

if [ -z "${2:-}" ]; then
  usage >&2; exit 1
fi
SIB_A="$1"
SIB_B="$2"; shift 2

PASS_A=""
PASS_B=""
need_value() {
  [ -n "${2:-}" ] || { echo "$1 requires a value" >&2; exit 1; }
  case "$2" in --*) echo "$1 requires a value, got option-like token: $2" >&2; exit 1 ;; esac
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --pass-a) need_value "$1" "${2:-}"; PASS_A="$2"; shift 2 ;;
    --pass-b) need_value "$1" "${2:-}"; PASS_B="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

A="$SIB_A/audit/agent_surfaces.jsonl"
B="$SIB_B/audit/agent_surfaces.jsonl"
[ -f "$A" ] || { echo "missing: $A" >&2; exit 1; }
[ -f "$B" ] || { echo "missing: $B" >&2; exit 1; }

[ -z "$PASS_A" ] && PASS_A=$(jq -r '.pass // 1' "$A" | sort -n | tail -1)
[ -z "$PASS_B" ] && PASS_B=$(jq -r '.pass // 1' "$B" | sort -n | tail -1)

# Filter both to their target passes.
TMP_A=$(mktemp /tmp/aerg_cmp_a.XXXXXX)
TMP_B=$(mktemp /tmp/aerg_cmp_b.XXXXXX)
jq -c --arg p "$PASS_A" 'select((.pass // 1) == ($p | tonumber))' "$A" > "$TMP_A"
jq -c --arg p "$PASS_B" 'select((.pass // 1) == ($p | tonumber))' "$B" > "$TMP_B"

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
cat <<EOF
# Audit Comparison

Generated: $NOW
- A: \`$A\` (pass $PASS_A)
- B: \`$B\` (pass $PASS_B)

EOF

# Surface set comparison.
SIDS_A=$(jq -r '.surface_id' "$TMP_A" | sort -u)
SIDS_B=$(jq -r '.surface_id' "$TMP_B" | sort -u)
BOTH=$(comm -12 <(echo "$SIDS_A") <(echo "$SIDS_B"))
ONLY_A=$(comm -23 <(echo "$SIDS_A") <(echo "$SIDS_B"))
ONLY_B=$(comm -13 <(echo "$SIDS_A") <(echo "$SIDS_B"))

cat <<EOF
## Surface set
- in both: $(echo "$BOTH" | grep -c .)
- only in A: $(echo "$ONLY_A" | grep -c .)
- only in B: $(echo "$ONLY_B" | grep -c .)

EOF

if [ -n "$ONLY_A" ]; then
  echo "### Surfaces dropped in B"
  while IFS= read -r sid; do
    printf -- '- %s\n' "$sid"
  done <<< "$ONLY_A"
  echo
fi
if [ -n "$ONLY_B" ]; then
  echo "### Surfaces added in B"
  while IFS= read -r sid; do
    printf -- '- %s\n' "$sid"
  done <<< "$ONLY_B"
  echo
fi

# Per-surface delta.
cat <<EOF
## Per-surface weighted_score delta (B − A)

| surface_id | A weighted | B weighted | Δ |
|------------|------------|------------|---|
EOF
while IFS= read -r sid; do
  [ -z "$sid" ] && continue
  wa=$(jq -r --arg s "$sid" 'select(.surface_id == $s) | .weighted_score // 0' "$TMP_A" | head -1)
  wb=$(jq -r --arg s "$sid" 'select(.surface_id == $s) | .weighted_score // 0' "$TMP_B" | head -1)
  delta=$((wb - wa))
  sign=""
  [ "$delta" -gt 0 ] && sign="+"
  printf '| %s | %s | %s | %s%s |\n' "$sid" "$wa" "$wb" "$sign" "$delta"
done <<< "$BOTH"

# Per-dim aggregate delta.
echo
cat <<EOF
## Per-dimension mean delta (B − A) across surfaces in both
EOF
echo
echo '| dim | A mean | B mean | Δ |'
echo '|-----|--------|--------|---|'
for dim in agent_intuitiveness agent_ergonomics agent_ease_of_use output_parseability error_pedagogy intent_inference safety_with_recovery determinism_and_reproducibility self_documentation composability regression_resistance; do
  a_mean=$(jq -r --arg d "$dim" --argjson sids "$(echo "$BOTH" | jq -R . | jq -s .)" \
           'select([.surface_id] | inside($sids)) | .scores[$d] // empty' "$TMP_A" \
         | awk 'NF { sum += $1; n++ } END { if (n>0) printf "%.0f", sum/n; else print "-" }')
  b_mean=$(jq -r --arg d "$dim" --argjson sids "$(echo "$BOTH" | jq -R . | jq -s .)" \
           'select([.surface_id] | inside($sids)) | .scores[$d] // empty' "$TMP_B" \
         | awk 'NF { sum += $1; n++ } END { if (n>0) printf "%.0f", sum/n; else print "-" }')
  if [ "$a_mean" = "-" ] || [ "$b_mean" = "-" ]; then
    delta="-"
    sign=""
  else
    delta=$((b_mean - a_mean))
    sign=""
    [ "$delta" -gt 0 ] && sign="+"
  fi
  printf '| %s | %s | %s | %s%s |\n' "$dim" "$a_mean" "$b_mean" "$sign" "$delta"
done

: > "$TMP_A"
: > "$TMP_B"
exit 0
