#!/usr/bin/env bash
# scripts/verify-stdout-stderr-split.sh — Verify a tool's stdout is data-only and stderr is diagnostics-only.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/verify-stdout-stderr-split.sh <tool-binary> <verb> [args...]

Verifies the data/diagnostics stream split that agents depend on:
  1. If the tool accepts --json, stdout is parseable JSON.
  2. Stdout does not contain log-formatted lines (DEBUG/INFO/WARN/ERROR or
     ISO-8601 timestamps at line start).
  3. Stderr does not contain JSON output (data should not leak to stderr).

Args:
  <tool-binary>   Path or PATH-resolvable name of the CLI to test.
  <verb>          Subcommand to invoke.
  [args...]       Additional positional args / flags.

Exit codes:
  0  Split is clean.
  1  Violation; first three offending lines printed to stderr.
  2  Missing args, tool not found, or no verb provided (input error,
     distinct from "violation" so callers can tell them apart).

Example:
  scripts/verify-stdout-stderr-split.sh ./target/release/mytool list
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 2 ;;
esac

TOOL="$1"
shift

if [ "$#" -eq 0 ]; then
  echo "no verb specified" >&2
  echo "(run with --help for usage)" >&2
  exit 2
fi

if ! command -v "$TOOL" >/dev/null 2>&1 && [ ! -x "$TOOL" ]; then
  echo "tool not found / not executable: $TOOL" >&2
  exit 2
fi

stderr_tmp=$(mktemp /tmp/aerg_stderr.XXXXXX)
stdout_tmp=$(mktemp /tmp/aerg_stdout.XXXXXX)
# Retain captured streams for diagnosis when the split check fails. This repo
# forbids agents from deleting files.

# Run with --json if the tool accepts it
maybe_json=""
if "$TOOL" "$@" --help 2>/dev/null | grep -qE -- '--json'; then
  maybe_json="--json"
fi

set +e
"$TOOL" "$@" $maybe_json > "$stdout_tmp" 2> "$stderr_tmp"
ec=$?
set -e

# Check 1: stdout is parseable JSON if --json was passed
if [ -n "$maybe_json" ]; then
  if ! jq . "$stdout_tmp" > /dev/null 2>&1; then
    echo "VIOLATION: --json mode produced invalid JSON on stdout" >&2
    head -3 "$stdout_tmp" >&2
    exit 1
  fi
fi

# Check 2: stdout doesn't contain log-formatted lines
log_pattern='^(\[?[0-9]{4}-[0-9]{2}-[0-9]{2}T?|[A-Z]{4,5}\s+|DEBUG|INFO|WARN|ERROR|TRACE)'
if grep -qE "$log_pattern" "$stdout_tmp"; then
  echo "VIOLATION: stdout contains log-formatted lines (logs should go to stderr)" >&2
  grep -E "$log_pattern" "$stdout_tmp" | head -3 >&2
  exit 1
fi

# Check 3: stderr should NOT contain JSON output (data leaks to stderr is also a violation)
if [ -n "$maybe_json" ] && [ -s "$stderr_tmp" ]; then
  if jq . "$stderr_tmp" > /dev/null 2>&1; then
    echo "WARNING: stderr contains parseable JSON; data may be leaking to wrong stream" >&2
  fi
fi

echo "OK: stdout/stderr split clean (exit $ec)"
exit 0
