#!/usr/bin/env bash
# scripts/verify-non-tty-discipline.sh — Verify a tool honors NO_COLOR, CI=true, piped stdout.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/verify-non-tty-discipline.sh <tool-binary> <verb> [args...]

Verifies that <tool-binary> behaves correctly when invoked from a non-TTY
context (the default for AI agents). Runs five independent tests:

  1. Piped stdout strips ANSI escape codes.
  2. NO_COLOR=1 strips ANSI.
  3. TERM=dumb strips ANSI.
  4. CI=true strips ANSI.
  5. Stdin closed (</dev/null) does not block on a prompt within 5s.

Args:
  <tool-binary>   Path or PATH-resolvable name of the CLI to test.
  <verb>          Subcommand to invoke.
  [args...]       Additional positional args / flags.

Exit codes:
  0  All tests pass.
  1  At least one violation; per-test stderr message printed.
  2  Missing args, tool not found, or no verb provided (input error,
     distinct from "violations found" so callers can tell them apart).

Example:
  scripts/verify-non-tty-discipline.sh ./target/release/mytool list
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

violations=0

# We deliberately swallow non-zero exits from the tool under test (it may legitimately
# exit non-zero on the verb being probed). Each test only cares about the captured
# stream content, not the process exit status — except test 5 (timeout detection).

# Test 1: piped stdout strips ANSI
out=$("$TOOL" "$@" 2>/dev/null | cat) || true
if echo "$out" | grep -qE $'\x1b\['; then
  echo "VIOLATION: piped stdout contains ANSI escape codes" >&2
  violations=$((violations + 1))
fi

# Test 2: NO_COLOR=1 strips ANSI
out=$(NO_COLOR=1 "$TOOL" "$@" 2>/dev/null) || true
if echo "$out" | grep -qE $'\x1b\['; then
  echo "VIOLATION: NO_COLOR=1 ignored" >&2
  violations=$((violations + 1))
fi

# Test 3: TERM=dumb strips ANSI
out=$(TERM=dumb "$TOOL" "$@" 2>/dev/null) || true
if echo "$out" | grep -qE $'\x1b\['; then
  echo "VIOLATION: TERM=dumb ignored" >&2
  violations=$((violations + 1))
fi

# Test 4: CI=true behavior — should match piped behavior
out_ci=$(CI=true "$TOOL" "$@" 2>/dev/null) || true
if echo "$out_ci" | grep -qE $'\x1b\['; then
  echo "VIOLATION: CI=true ignored (ANSI still in stdout)" >&2
  violations=$((violations + 1))
fi

# Test 5: stdin closed (non-blocking — tool must not prompt)
ec=0
out=$(timeout 5 "$TOOL" "$@" </dev/null 2>/dev/null) || ec=$?
if [ "$ec" -eq 124 ]; then
  echo "VIOLATION: tool blocked on stdin (timeout fired); likely tries to prompt in non-TTY context" >&2
  violations=$((violations + 1))
fi

if [ "$violations" -gt 0 ]; then
  echo "$violations violation(s) found" >&2
  exit 1
fi

echo "OK: non-TTY discipline clean"
exit 0
