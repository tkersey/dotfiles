#!/usr/bin/env bash
# scripts/verify-determinism.sh — Verify a tool's --json output is deterministic across re-runs.
# Strips known volatile fields (request_id, timestamps) before comparing.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/verify-determinism.sh <tool-binary> <verb> [args...]

Runs <tool-binary> <verb> [args...] --json twice in a row with
SOURCE_DATE_EPOCH=1234567890 pinned, strips known volatile fields
(request_id, ts_iso, elapsed_ms, etag) from both outputs, and reports
"OK" if the two outputs are byte-identical.

Args:
  <tool-binary>   Path or PATH-resolvable name of the CLI to test.
  <verb>          The subcommand to invoke (e.g. "list", "status").
  [args...]       Any additional positional args / flags for the verb.

Exit codes:
  0  Outputs match → tool is deterministic on this verb.
  1  Outputs differ → first 20 lines of diff printed to stderr.
  2  Missing args, tool not found, or no verb provided (input error,
     distinct from "outputs differ" so callers can tell them apart).

Example:
  scripts/verify-determinism.sh ./target/release/mytool list --filter active
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

# Honor SOURCE_DATE_EPOCH so timestamp-based fields are pinned
export SOURCE_DATE_EPOCH=1234567890

run1=$(mktemp /tmp/aerg_run1.XXXXXX)
run2=$(mktemp /tmp/aerg_run2.XXXXXX)
# Retain captured outputs for diagnosis when determinism fails. This repo
# forbids agents from deleting files.

# Two consecutive invocations
"$TOOL" "$@" --json > "$run1" 2>/dev/null
"$TOOL" "$@" --json > "$run2" 2>/dev/null

# Strip volatile fields with jq
canonicalize() {
  jq 'walk(if type=="object" then del(.meta.request_id, .meta.ts_iso, .meta.elapsed_ms, .meta.ran_at, .request_id, .ts, .timestamp, ._etag) else . end)' < "$1"
}

c1=$(canonicalize "$run1")
c2=$(canonicalize "$run2")

if [ "$c1" != "$c2" ]; then
  echo "VIOLATION: output differs across re-runs (after stripping volatile fields)" >&2
  diff <(echo "$c1") <(echo "$c2") | head -20 >&2 || true
  exit 1
fi

# Bonus: verify SOURCE_DATE_EPOCH was honored (timestamps should reflect the pinned
# epoch). The pinned epoch is 1234567890 → 2009-02-13. If the output contains a
# timestamp from the *current* year, the tool likely ignored SOURCE_DATE_EPOCH.
# `\s` is Perl-only and not portable across grep implementations — use POSIX class.
current_year=$(date -u +%Y)
if echo "$c1" | grep -qE "\"ts(_iso)?\"[[:space:]]*:[[:space:]]*\"${current_year}" ; then
  echo "WARNING: stdout has ${current_year}-flavored timestamps despite SOURCE_DATE_EPOCH=1234567890; tool may not honor SOURCE_DATE_EPOCH" >&2
fi

echo "OK: deterministic across re-runs"
exit 0
