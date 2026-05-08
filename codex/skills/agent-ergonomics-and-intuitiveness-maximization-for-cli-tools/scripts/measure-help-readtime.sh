#!/usr/bin/env bash
# scripts/measure-help-readtime.sh — Estimate how long an agent takes to "read" --help
# (proxy: line count + token count + structural complexity).
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/measure-help-readtime.sh <tool-binary>

Estimates the cognitive cost of <tool> --help for an agent. Counts lines,
words, characters, estimates tokens (~5 chars/token), and projects read time
at ~50 tokens/second. Detects structural signals (TOC, examples, agent
footer) and emits a verdict (concise / moderate / long / excessive).

Args:
  <tool-binary>   Path or PATH-resolvable name of the CLI to test.

Output:
  Single JSON object on stdout.

Exit codes:
  0  Success.
  1  Missing arguments (usage printed).
  2  Tool not found or not executable.

Example:
  scripts/measure-help-readtime.sh ./target/release/mytool | jq .verdict
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

TOOL="$1"

if ! command -v "$TOOL" >/dev/null 2>&1 && [ ! -x "$TOOL" ]; then
  echo "tool not found / not executable: $TOOL" >&2
  exit 2
fi

help_out=$(timeout 5 "$TOOL" --help 2>&1)
lines=$(echo "$help_out" | wc -l)
words=$(echo "$help_out" | wc -w)
chars=${#help_out}
# Estimate: ~5 chars/token; agents read at ~50 tokens/s.
# Force LC_NUMERIC=C so awk emits "2.9" not "2,9" in locales where decimal sep differs.
tokens_est=$((chars / 5))
read_time_s=$(LC_NUMERIC=C awk -v t="$tokens_est" 'BEGIN { printf "%.1f", t / 50 }')

# Structural signals
has_toc=$(echo "$help_out" | grep -qE '<!-- TOC|## ' && echo true || echo false)
has_examples=$(echo "$help_out" | grep -qiE 'example' && echo true || echo false)
has_agent_footer=$(echo "$help_out" | grep -qiE 'AGENT|--robot|capabilities --json|robot-docs' && echo true || echo false)

# Verdict
if [ "$lines" -lt 30 ]; then
  verdict="concise (smaller-agent-friendly)"
elif [ "$lines" -lt 100 ]; then
  verdict="moderate"
elif [ "$lines" -lt 300 ]; then
  verdict="long (consider TOC + cheat sheet)"
else
  verdict="excessive (agents will skim or skip)"
fi

cat <<EOF
{
  "tool":             "$TOOL",
  "lines":            $lines,
  "words":            $words,
  "chars":            $chars,
  "tokens_estimated": $tokens_est,
  "read_time_seconds_estimated": $read_time_s,
  "has_toc":          $has_toc,
  "has_examples":     $has_examples,
  "has_agent_footer": $has_agent_footer,
  "verdict":          "$verdict"
}
EOF
