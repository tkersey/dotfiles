#!/usr/bin/env bash
# scripts/replay_simulation.sh — Replay a captured simulation transcript against the current binary.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/replay_simulation.sh <transcript.jsonl> <tool-binary>

Replays a captured Phase 3 / Phase 9 simulation transcript against the
current build of <tool-binary>. For each step in the transcript, re-runs
the captured argv with argv[0] replaced by <tool-binary>, then diffs the new
exit code + stdout (after stripping known volatile fields like timestamps and
request IDs) against the captured outcome. Emits a "DRIFT" entry per
mismatched step. Legacy invocation strings are replayed only if they contain
simple whitespace-separated tokens with no shell metacharacters.

Args:
  <transcript.jsonl>   A captured transcript from
                       audit/agent_simulations/<stage>_pass_<N>/.
  <tool-binary>        The current build to test against.

Exit codes:
  0  No drift.
  1  At least one step drifted (lines printed to stdout).
  2  Missing args, or transcript file not found (input error, distinct
     from "drift detected" so callers can tell them apart).

Example:
  scripts/replay_simulation.sh \
    audit/agent_simulations/post_pass_1/task-01-list.transcript.jsonl \
    ./target/release/mytool
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 2 ;;
esac

if [ -z "${2:-}" ]; then
  usage >&2
  exit 2
fi

TRANSCRIPT="$1"
TOOL="$2"

if [ ! -f "$TRANSCRIPT" ]; then
  echo "transcript not found: $TRANSCRIPT" >&2
  exit 2
fi

TRANSCRIPT_DIR="$(cd "$(dirname "$TRANSCRIPT")" && pwd)"
ALLOWED_CWD_ROOT="$TRANSCRIPT_DIR"
probe="$TRANSCRIPT_DIR"
while [ "$probe" != "/" ]; do
  if [ -f "$probe/audit/manifest.json" ]; then
    ALLOWED_CWD_ROOT="$probe"
    break
  fi
  if [ "$(basename "$probe")" = "audit" ] && [ -f "$probe/manifest.json" ]; then
    ALLOWED_CWD_ROOT="$(cd "$probe/.." && pwd)"
    break
  fi
  probe="$(dirname "$probe")"
done
ALLOWED_CWD_REAL=$(/usr/bin/realpath -m "$ALLOWED_CWD_ROOT" 2>/dev/null || echo "$ALLOWED_CWD_ROOT")

echo "Replaying $TRANSCRIPT against $TOOL"
echo

drift=0
total=0
unreplayable=0

deny_env_key() {
  local key="$1"
  [[ "$key" =~ ^(LD_|DYLD_|GLIBC_|MALLOC_|TMP|TMPDIR|HOME|USER|UID|GID|PATH|MANPATH|LIBRARY_PATH|PYTHONPATH|PERL5LIB|RUBYLIB|NODE_PATH|NODE_OPTIONS|JAVA_TOOL_OPTIONS|SSL_CERT_|GIT_|SSH_|GPG_|SUDO_|ASAN_|TSAN_|MSAN_|UBSAN_) ]]
}

has_unsafe_shell_syntax() {
  local s="$1"
  [[ "$s" == *'$'* ]] && return 0
  [[ "$s" == *'`'* ]] && return 0
  [[ "$s" == *';'* ]] && return 0
  [[ "$s" == *'&'* ]] && return 0
  [[ "$s" == *'|'* ]] && return 0
  [[ "$s" == *'<'* ]] && return 0
  [[ "$s" == *'>'* ]] && return 0
  [[ "$s" == *'('* ]] && return 0
  [[ "$s" == *')'* ]] && return 0
  [[ "$s" == *'{'* ]] && return 0
  [[ "$s" == *'}'* ]] && return 0
  [[ "$s" == *'['* ]] && return 0
  [[ "$s" == *']'* ]] && return 0
  [[ "$s" == *'*'* ]] && return 0
  [[ "$s" == *'?'* ]] && return 0
  [[ "$s" == *'!'* ]] && return 0
  [[ "$s" == *'~'* ]] && return 0
  [[ "$s" == *'"'* ]] && return 0
  [[ "$s" == *"'"* ]] && return 0
  [[ "$s" == *"\\"* ]] && return 0
  return 1
}

row_to_argv() {
  local row="$1" invocation="$2"
  if echo "$row" | jq -e '(.argv // null) | type == "array" and length > 0' >/dev/null 2>&1; then
    echo "$row" | jq -r --arg tool "$TOOL" '[$tool] + ((.argv[1:] // []) | map(tostring)) | .[]'
    return 0
  fi

  if has_unsafe_shell_syntax "$invocation"; then
    return 3
  fi

  local parts=()
  read -r -a parts <<< "$invocation"
  [ "${#parts[@]}" -gt 0 ] || return 3
  printf '%s\n' "$TOOL"
  local i
  for ((i = 1; i < ${#parts[@]}; i++)); do
    printf '%s\n' "${parts[$i]}"
  done
}

while IFS= read -r line; do
  [ -z "$line" ] && continue
  step=$(echo "$line" | jq -r '.step')
  invocation=$(echo "$line" | jq -r '.invocation // ""')
  captured_exit=$(echo "$line" | jq -r '.exit_code')
  captured_stdout=$(echo "$line" | jq -r '.stdout')
  cwd=$(echo "$line" | jq -r '.cwd // ""')

  argv=()
  if [ -n "$cwd" ] && [ ! -d "$cwd" ]; then
    total=$((total + 1))
    unreplayable=$((unreplayable + 1))
    drift=$((drift + 1))
    echo "UNREPLAYABLE step $step: cwd does not exist: $cwd"
    echo
    continue
  elif [ -n "$cwd" ]; then
    cwd_real=$(/usr/bin/realpath -m "$cwd" 2>/dev/null || echo "$cwd")
    case "$cwd_real" in
      "$ALLOWED_CWD_REAL"|"$ALLOWED_CWD_REAL"/*)
        : ;;
      *)
        total=$((total + 1))
        unreplayable=$((unreplayable + 1))
        drift=$((drift + 1))
        echo "UNREPLAYABLE step $step: cwd outside audit workspace: $cwd"
        echo "  replay only permits cwd under $ALLOWED_CWD_ROOT"
        echo
        continue
        ;;
    esac
  fi

  # Capture row_to_argv's stdout AND status. `mapfile < <(...)` reports only
  # mapfile's status, which would hide an unsafe legacy invocation failure.
  set +e
  argv_out=$(row_to_argv "$line" "$invocation")
  argv_rc=$?
  set -e
  if [ "$argv_rc" -ne 0 ]; then
    total=$((total + 1))
    unreplayable=$((unreplayable + 1))
    drift=$((drift + 1))
    echo "UNREPLAYABLE step $step: legacy invocation missing or contains shell syntax; transcript needs argv[]"
    echo "  invocation: $invocation"
    echo
    continue
  fi
  mapfile -t argv <<< "$argv_out"

  env_args=("NO_COLOR=1" "TERM=dumb" "CI=true")
  while IFS= read -r env_kv; do
    [ -z "$env_kv" ] && continue
    env_key="${env_kv%%=*}"
    if deny_env_key "$env_key"; then
      echo "skipping unsafe env key '$env_key' from transcript step $step" >&2
      continue
    fi
    if ! [[ "$env_key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
      echo "skipping malformed env key '$env_key' from transcript step $step" >&2
      continue
    fi
    env_args+=("$env_kv")
  done < <(echo "$line" | jq -r '.env // {} | to_entries[] | "\(.key)=\(.value|tostring)"')

  # Re-run without a shell so transcript arguments cannot execute metacharacters.
  set +e
  if [ -n "$cwd" ]; then
    new_stdout=$(cd "$cwd" && env "${env_args[@]}" timeout 10 "${argv[@]}" </dev/null 2>/dev/null)
  else
    new_stdout=$(env "${env_args[@]}" timeout 10 "${argv[@]}" </dev/null 2>/dev/null)
  fi
  new_exit=$?
  set -e

  total=$((total + 1))

  # Strip volatile fields before comparing (timestamps, request_ids)
  captured_norm=$(echo "$captured_stdout" | sed -E 's/[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.Z+-]+//g; s/req_[a-zA-Z0-9]+//g')
  new_norm=$(echo "$new_stdout" | sed -E 's/[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.Z+-]+//g; s/req_[a-zA-Z0-9]+//g')

  if [ "$new_exit" != "$captured_exit" ] || [ "$new_norm" != "$captured_norm" ]; then
    drift=$((drift + 1))
    echo "DRIFT step $step: $invocation"
    echo "  exit: captured=$captured_exit new=$new_exit"
    if [ "$new_norm" != "$captured_norm" ]; then
      diff <(echo "$captured_norm") <(echo "$new_norm") | head -20 || true
    fi
    echo
  fi
done < "$TRANSCRIPT"

echo "Replay summary: $total steps, $drift drifted, $unreplayable unreplayable"
[ "$drift" -gt 0 ] && exit 1 || exit 0
