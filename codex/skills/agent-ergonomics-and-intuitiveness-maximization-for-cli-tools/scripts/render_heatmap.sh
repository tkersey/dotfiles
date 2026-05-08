#!/usr/bin/env bash
# scripts/render_heatmap.sh — Render agent_surfaces.jsonl → SVG heatmap.
# Surfaces are rows; dimensions are columns. Color: red (low) → green (high).
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/render_heatmap.sh <agent_surfaces.jsonl> [--pass N | --all-passes]

Renders an SVG heatmap of surfaces × the 11 scoring dimensions. Cells are
colored: red (low score, ergonomic gap) → yellow → green (high). Cell text
shows the integer score; missing scores render gray.

Args:
  <agent_surfaces.jsonl>   Phase 2 / Phase 6 scoring output.
  --pass N                 Filter to records where .pass == N.
  --all-passes             Show every record in the file (no filter).

Default behavior (no flag): filter to the **latest pass** in the file.
This avoids duplicate per-surface rows in multi-pass workspaces.

Output:
  SVG document on stdout. Redirect to <sibling>/audit/heatmap.svg.

Example:
  scripts/render_heatmap.sh audit/agent_surfaces.jsonl --pass 2 \
    > audit/heatmap.svg

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
  [ -n "${2:-}" ] || { echo "render_heatmap: $1 requires a value" >&2; exit 1; }
  case "$2" in --*) echo "render_heatmap: $1 requires a value, got option-like token: $2" >&2; exit 1 ;; esac
}
case "${2:-}" in
  "") ;;
  --pass)
    need_value "$2" "${3:-}"
    if [ -n "${4:-}" ]; then
      echo "render_heatmap: unexpected extra argument: $4" >&2
      usage >&2
      exit 1
    fi
    PASS_FILTER="$3"
    ;;
  --all-passes)
    if [ -n "${3:-}" ]; then
      echo "render_heatmap: unexpected extra argument: $3" >&2
      usage >&2
      exit 1
    fi
    ALL_PASSES=true
    ;;
  *)
    echo "render_heatmap: unknown argument: $2" >&2
    usage >&2
    exit 1
    ;;
esac

if [ ! -f "$JSONL" ]; then
  echo "<!-- heatmap input not found: $JSONL -->" >&2
  exit 2
fi

TMP_JSONL=""
# shellcheck disable=SC2317 # Invoked by EXIT trap; truncates scratch file per repo no-deletion policy.
cleanup() { [ -n "$TMP_JSONL" ] && [ -f "$TMP_JSONL" ] && : > "$TMP_JSONL"; }
trap cleanup EXIT

# Default: show only the latest pass in the file. A multi-pass workspace
# would otherwise paint a heatmap with duplicate rows per surface (one per
# pass), which makes the visual signal misleading. `--all-passes` keeps the
# original behavior for cross-pass review.
if [ -z "$PASS_FILTER" ] && [ "$ALL_PASSES" = false ]; then
  PASS_FILTER=$(jq -r '.pass // 1' "$JSONL" | sort -n | tail -1)
fi

if [ -n "$PASS_FILTER" ]; then
  TMP_JSONL=$(mktemp /tmp/aerg_heatmap.XXXXXX)
  jq -c --arg pass "$PASS_FILTER" 'select((.pass // 1) == ($pass | tonumber))' "$JSONL" > "$TMP_JSONL"
  JSONL="$TMP_JSONL"
  # If the filter matched zero rows, the heatmap renders as a single empty
  # row with default-color cells — a silent visual failure that's hard to
  # tell apart from a real "all-grey" pass. Surface the mismatch on stderr
  # so a caller passing the wrong --pass N gets a clear signal.
  if ! [ -s "$JSONL" ]; then
    echo "render_heatmap: no rows match pass $PASS_FILTER (rendering empty heatmap)" >&2
  fi
fi

DIMS=(agent_intuitiveness agent_ergonomics agent_ease_of_use output_parseability error_pedagogy intent_inference safety_with_recovery determinism_and_reproducibility self_documentation composability regression_resistance)

CELL_W=80
CELL_H=24
LABEL_W=300
HEADER_H=120

NUM_SURFACES=$(wc -l < "$JSONL")
[ "$NUM_SURFACES" -lt 1 ] && NUM_SURFACES=1
NUM_DIMS=${#DIMS[@]}
SVG_W=$(( LABEL_W + NUM_DIMS * CELL_W + 20 ))
SVG_H=$(( HEADER_H + NUM_SURFACES * CELL_H + 60 ))

# Color helper: 0 → red(220,60,60), 500 → yellow(220,200,60), 1000 → green(60,200,80)
score_to_rgb() {
  local s="$1"
  if [ -z "$s" ] || [ "$s" = "null" ]; then echo "200,200,200"; return; fi
  # Defensive: only proceed if integer
  if ! [[ "$s" =~ ^[0-9]+$ ]]; then echo "200,200,200"; return; fi
  if [ "$s" -le 500 ]; then
    local g=$(( 60 + (200 - 60) * s / 500 ))
    echo "220,$g,60"
  else
    local r=$(( 220 - (220 - 60) * (s - 500) / 500 ))
    local b=$(( 60 + (80 - 60) * (s - 500) / 500 ))
    echo "$r,200,$b"
  fi
}

xml_escape() {
  sed \
    -e 's/&/\&amp;/g' \
    -e 's/</\&lt;/g' \
    -e 's/>/\&gt;/g' \
    -e 's/"/\&quot;/g' \
    -e "s/'/\&apos;/g"
}

# SVG header
cat <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="$SVG_W" height="$SVG_H" font-family="ui-monospace,Menlo,monospace" font-size="11">
  <style>
    text { dominant-baseline: middle; }
    .surface_id { text-anchor: end; fill: #333; }
    .dim_label { fill: #333; }
    .cell_text { text-anchor: middle; fill: #000; font-size: 9px; }
    .header { font-weight: bold; fill: #111; }
  </style>
EOF

# Column headers (dimensions)
short_dims=(intu ergo ease parse error intent safe det self comp regr)
for i in "${!DIMS[@]}"; do
  x=$(( LABEL_W + i * CELL_W + CELL_W / 2 ))
  y=$(( HEADER_H - 10 ))
  printf '  <g transform="translate(%d %d) rotate(-45)"><text class="header" x="0" y="0">%s</text></g>\n' "$x" "$y" "${short_dims[$i]}"
done

# Row labels + cells
y=$HEADER_H
while IFS= read -r line; do
  surface_id=$(echo "$line" | jq -r '.surface_id')
  surface_label=$(printf '%s' "$surface_id" | xml_escape)
  printf '  <text class="surface_id" x="%d" y="%d">%s</text>\n' "$((LABEL_W - 8))" "$((y + CELL_H / 2))" "$surface_label"
  for i in "${!DIMS[@]}"; do
    dim="${DIMS[$i]}"
    score=$(echo "$line" | jq -r ".scores.\"$dim\" // empty")
    rgb=$(score_to_rgb "${score:-500}")
    x=$(( LABEL_W + i * CELL_W ))
    printf '  <rect x="%d" y="%d" width="%d" height="%d" fill="rgb(%s)" stroke="#fff"/>\n' "$x" "$y" "$CELL_W" "$CELL_H" "$rgb"
    if [ -n "$score" ] && [ "$score" != "null" ]; then
      printf '  <text class="cell_text" x="%d" y="%d">%s</text>\n' "$((x + CELL_W / 2))" "$((y + CELL_H / 2))" "$score"
    fi
  done
  y=$((y + CELL_H))
done < "$JSONL"

# Legend
LEGEND_Y=$((y + 20))
cat <<EOF
  <text x="$LABEL_W" y="$LEGEND_Y" class="header">Legend:</text>
  <rect x="$((LABEL_W + 80))" y="$((LEGEND_Y - 8))" width="40" height="16" fill="rgb(220,60,60)" />
  <text x="$((LABEL_W + 130))" y="$LEGEND_Y" fill="#333">0 (worst)</text>
  <rect x="$((LABEL_W + 220))" y="$((LEGEND_Y - 8))" width="40" height="16" fill="rgb(220,200,60)" />
  <text x="$((LABEL_W + 270))" y="$LEGEND_Y" fill="#333">500</text>
  <rect x="$((LABEL_W + 340))" y="$((LEGEND_Y - 8))" width="40" height="16" fill="rgb(60,200,80)" />
  <text x="$((LABEL_W + 390))" y="$LEGEND_Y" fill="#333">1000 (best)</text>
</svg>
EOF

exit 0
