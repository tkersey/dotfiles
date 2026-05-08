#!/usr/bin/env bash
# scripts/render_scorecard.sh — Render agent_surfaces.jsonl → markdown scorecard.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/render_scorecard.sh <agent_surfaces.jsonl> [--pass N | --all-passes]

Renders an agent_surfaces.jsonl scorecard (Phase 2/6 output) into a human-
readable markdown scorecard with per-surface table, weighted-score histogram,
and a "below Polish Bar (< 750)" list.

Args:
  <agent_surfaces.jsonl>   Phase 2 / Phase 6 scoring output (one record per
                           surface_id × pass).
  --pass N                 Filter to records where .pass == N. Use this for
                           per-pass historical scorecards.
  --all-passes             Show every record in the file (no filter). Useful
                           for manual cross-pass review; for diff between
                           passes prefer `tools/diff_scorecards.sh`.

Default behavior (no flag): filter to the **latest pass** found in the file.
This avoids duplicate surface_id rows in multi-pass workspaces.

Output:
  Markdown to stdout. Redirect to <sibling>/audit/scorecard.md or
  scorecard_pass_<N>.md.

Example:
  scripts/render_scorecard.sh audit/agent_surfaces.jsonl --pass 2 \
    > audit/scorecard_pass_2.md

Exit codes:
  0  Success.
  1  Missing arguments (usage printed).
  2  Input file not found.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

JSONL="$1"
PASS_FILTER=""
ALL_PASSES=false
need_value() {
  [ -n "${2:-}" ] || { echo "render_scorecard: $1 requires a value" >&2; exit 1; }
  case "$2" in --*) echo "render_scorecard: $1 requires a value, got option-like token: $2" >&2; exit 1 ;; esac
}
case "${2:-}" in
  "") ;;
  --pass)
    need_value "$2" "${3:-}"
    if [ -n "${4:-}" ]; then
      echo "render_scorecard: unexpected extra argument: $4" >&2
      usage >&2
      exit 1
    fi
    PASS_FILTER="$3"
    ;;
  --all-passes)
    if [ -n "${3:-}" ]; then
      echo "render_scorecard: unexpected extra argument: $3" >&2
      usage >&2
      exit 1
    fi
    ALL_PASSES=true
    ;;
  *)
    echo "render_scorecard: unknown argument: $2" >&2
    usage >&2
    exit 1
    ;;
esac

if [ ! -f "$JSONL" ]; then
  echo "scorecard input not found: $JSONL" >&2
  exit 2
fi

# Filter by pass. Default behavior: show only the latest pass found in the file
# (otherwise multi-pass workspaces produce duplicate surface_id rows — one per
# pass — which is confusing when reading "the current scorecard"). Pass
# `--all-passes` to keep the original "show every record" behavior, e.g. for
# manual cross-pass review.
TMP_JSONL=""
# shellcheck disable=SC2317 # Invoked by EXIT trap; truncates scratch file per repo no-deletion policy.
cleanup() { [ -n "$TMP_JSONL" ] && [ -f "$TMP_JSONL" ] && : > "$TMP_JSONL"; }
trap cleanup EXIT

# Preserve the user-supplied path for the "Source:" header — once we filter
# by pass, $JSONL is reassigned to the mktemp scratch file and the rendered
# scorecard would otherwise advertise an opaque /tmp/aerg_scorecard.XXXXXX
# path that the user never typed.
SOURCE_PATH="$JSONL"

if [ -z "$PASS_FILTER" ] && [ "$ALL_PASSES" = false ]; then
  # No explicit filter → default to latest pass in the file.
  PASS_FILTER=$(jq -r '.pass // 1' "$JSONL" | sort -n | tail -1)
fi

if [ -n "$PASS_FILTER" ]; then
  TMP_JSONL=$(mktemp /tmp/aerg_scorecard.XXXXXX)
  jq -c --arg pass "$PASS_FILTER" 'select((.pass // 1) == ($pass | tonumber))' "$JSONL" > "$TMP_JSONL"
  JSONL="$TMP_JSONL"
  # If the filter matched nothing, surface that to the user (and to stderr
  # so callers can detect it). Don't fail — the scorecard still renders, but
  # with a header that explicitly says "no rows" instead of leaving the
  # reader to puzzle over an empty table and an empty histogram.
  if ! [ -s "$JSONL" ]; then
    echo "render_scorecard: no rows match pass $PASS_FILTER (showing empty scorecard)" >&2
  fi
fi

cat <<EOF
# Agent Ergonomics Scorecard

Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Source: \`$SOURCE_PATH\`${PASS_FILTER:+ (pass $PASS_FILTER)}

EOF

# Per-surface table
echo
echo '## Per-surface scores'
echo
echo '| surface_id | weighted | intu | ergo | ease | parse | error | intent | safe | det | self | comp | regr |'
echo '|------------|----------|------|------|------|-------|-------|--------|------|-----|------|------|------|'

jq -r '
  [
    .surface_id,
    (.weighted_score // "-"),
    (.scores.agent_intuitiveness // "-"),
    (.scores.agent_ergonomics // "-"),
    (.scores.agent_ease_of_use // "-"),
    (.scores.output_parseability // "-"),
    (.scores.error_pedagogy // "-"),
    (.scores.intent_inference // "-"),
    (.scores.safety_with_recovery // "-"),
    (.scores.determinism_and_reproducibility // "-"),
    (.scores.self_documentation // "-"),
    (.scores.composability // "-"),
    (.scores.regression_resistance // "-")
  ] | @tsv
' "$JSONL" | awk -F'\t' '
  function md_cell(s) {
    gsub(/\|/, "\\|", s);
    return s;
  }
  {
    printf "| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |\n", md_cell($1), md_cell($2), md_cell($3), md_cell($4), md_cell($5), md_cell($6), md_cell($7), md_cell($8), md_cell($9), md_cell($10), md_cell($11), md_cell($12), md_cell($13)
  }'

echo
echo '## Distribution histogram'
echo
echo '### Weighted score distribution (per surface)'
echo
echo '```'
jq -r '.weighted_score // 0' "$JSONL" | awk '
  {
    s = $1 + 0;
    if (s >= 1000) bucket = 1000;
    else           bucket = int(s / 100) * 100;
    counts[bucket]++;
  }
  END {
    for (b = 0; b <= 1000; b += 100) {
      n = counts[b] + 0;
      bar = "";
      for (i = 0; i < n; i++) bar = bar "█";
      if (b == 1000) {
        printf "%4d     │ %s (%d)\n", b, bar, n;
      } else {
        printf "%4d-%3d │ %s (%d)\n", b, b+99, bar, n;
      }
    }
  }
'
echo '```'

echo
echo '## Below-Polish-Bar surfaces (weighted < 750)'
echo
jq -r 'select((.weighted_score // 0) < 750) | "- " + (.surface_id | gsub("\\|"; "\\|")) + " (weighted: " + ((.weighted_score // 0) | tostring) + ")"' "$JSONL"

exit 0
