#!/usr/bin/env bash
# tools/telemetry-summary.sh — Aggregate audit/telemetry.jsonl into a per-phase + per-subagent cost/duration summary.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/telemetry-summary.sh <sibling>

Reads <sibling>/audit/telemetry.jsonl and prints:
  - Per-phase: subagent count, total tokens (in/out), wall-time
  - Per-subagent: invocation count, tokens, mean duration, error rate
  - Outliers: any subagent invocation > 2× mean duration for its kind

Exit codes:
  0  Summary printed.
  1  Bad args / missing telemetry.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

SIBLING="$1"
TEL="$SIBLING/audit/telemetry.jsonl"

if [ ! -f "$TEL" ]; then
  echo "no telemetry yet: $TEL" >&2
  echo "(subagents call scripts/log-telemetry.sh on completion to populate this)" >&2
  exit 1
fi

if [ ! -s "$TEL" ]; then
  echo "telemetry empty: $TEL" >&2
  exit 0
fi

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
total=$(/usr/bin/wc -l < "$TEL")

cat <<EOF
# Telemetry Summary

Generated: $NOW
Source: \`$TEL\`
Total records: $total

EOF

echo "## Per-phase aggregates"
echo
echo "| phase | invocations | total_tokens | mean_duration_s | errors |"
echo "|-------|-------------|--------------|-----------------|--------|"
jq -s -r '
  group_by(.phase)
  | map({
      phase: .[0].phase,
      n: length,
      tokens: (map((.input_tokens // 0) + (.output_tokens // 0)) | add),
      mean_dur: ((map(.duration_s // 0) | add) / length | floor),
      errors: (map(select(.exit_status != 0)) | length)
    })
  | sort_by(.phase)
  | .[]
  | "| \(.phase) | \(.n) | \(.tokens) | \(.mean_dur) | \(.errors) |"
' "$TEL"

echo
echo "## Per-subagent aggregates"
echo
echo "| subagent | invocations | total_tokens | mean_duration_s | errors |"
echo "|----------|-------------|--------------|-----------------|--------|"
jq -s -r '
  group_by(.subagent)
  | map({
      subagent: .[0].subagent,
      n: length,
      tokens: (map((.input_tokens // 0) + (.output_tokens // 0)) | add),
      mean_dur: ((map(.duration_s // 0) | add) / length | floor),
      errors: (map(select(.exit_status != 0)) | length)
    })
  | sort_by(-.n)
  | .[]
  | "| \(.subagent) | \(.n) | \(.tokens) | \(.mean_dur) | \(.errors) |"
' "$TEL"

# Outliers: invocations > 2× mean duration for their subagent.
echo
echo "## Slow outliers (invocation duration > 2× mean for that subagent)"
jq -s -r '
  group_by(.subagent) as $groups
  | $groups[]
  | (.[0].subagent) as $name
  | ((map(.duration_s // 0) | add) / length) as $mean
  | .[]
  | select((.duration_s // 0) > $mean * 2 and (.duration_s // 0) > 30)
  | "- \($name) on \(.surface_id // "(global)"): \(.duration_s)s (\($mean | floor)s mean)"
' "$TEL" | head -20

# Cost projection. Use awk for float math — bc may be missing on minimal
# images (alpine, distroless) and falling back to bash arithmetic on token
# counts that exceed 2^63 isn't worth the complexity.
total_tokens=$(jq -s '[.[] | (.input_tokens // 0) + (.output_tokens // 0)] | add // 0' "$TEL")
read -r total_tokens_m cost_usd < <(awk -v t="$total_tokens" 'BEGIN { printf "%.2f %.2f\n", t/1000000, t/1000000*7.50 }')
echo
echo "## Cumulative cost"
echo
echo "- Total tokens: ~${total_tokens_m}M"
echo "- Estimated USD: \$${cost_usd} (at \$7.50/M)"

exit 0
