#!/usr/bin/env bash
# scripts/run_intent_corpus.sh — Run every corpus entry against the binary; classify outcome.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_intent_corpus.sh <sibling> <tool>

Phase 3 runner: invokes every corpus entry in <sibling>/audit/partial/
intent_naive.jsonl and intent_savvy.jsonl against <tool>, classifies each
outcome (silent_fail / useless_error / useful_hint / inferred_and_acted /
skipped), and writes <sibling>/audit/intent_inference_corpus.jsonl with results.

Entries should include an argv array. argv[0] is display-only and is replaced
with <tool> at runtime, so replay always targets the binary passed to this
script. Legacy invocation strings are accepted only when they contain simple
whitespace-separated tokens with no shell metacharacters.

Each invocation runs without a shell, with stdin closed, NO_COLOR=1, TERM=dumb,
CI=true, and a 5s timeout. Stdout/stderr are captured and truncated to 4096
bytes.

Args:
  <sibling>   Audit workspace root.
  <tool>      Path to the CLI binary to test against.

Output:
  Writes audit/intent_inference_corpus.jsonl. Per-class counts to stderr.

Exit codes:
  0  Success (corpus run complete; non-zero classifications are findings,
     not errors).
  1  Missing or invalid arguments (usage printed).

Example:
  scripts/run_intent_corpus.sh \
    /path/to/mytool__agent_ergonomics_audit \
    /path/to/mytool/target/release/mytool
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

if [ -z "${2:-}" ]; then
  usage >&2
  exit 1
fi

SIBLING="$1"
TOOL="$2"
AUDIT="$SIBLING/audit"
mkdir -p "$AUDIT"
OUT="$AUDIT/intent_inference_corpus.jsonl"

# Concurrent-run guard: refuse to start if another run_intent_corpus is
# in flight against the same workspace. Without this, two parents that
# both run Phase 3 (e.g. user opened the skill in two terminals, didn't
# notice) each truncate via `: > "$OUT"` and then append at different
# rates — the slower one's output can be partially overwritten by the
# faster one's truncate, producing a half-merged corpus that no consumer
# can detect as corrupt. The flock makes the second invocation either
# wait for the first to finish, or (with -n) fail fast with a clear
# error.
LOCK="${OUT}.lock"
exec 9>"$LOCK"
if command -v flock >/dev/null 2>&1; then
	if ! flock -n 9; then
		echo "another run_intent_corpus.sh is already running against $AUDIT" >&2
		echo "(wait for it to finish, or use the audit-doctor/truncation workflow for an orphaned lock; do not delete files unless repo rules explicitly allow it)" >&2
		exit 1
	fi
fi
: > "$OUT"

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

classify() {
  local exit_code="$1" stdout="$2" stderr="$3"
  if [ "$exit_code" -eq 0 ] && [ -z "$stdout" ] && [ -z "$stderr" ]; then
    echo "silent_fail"; return
  fi
  # useful_hint = tool errored AND its message points the agent toward the
  # right invocation. Real-world tools phrase this many ways:
  #   "did you mean --json?"          (rust/clap)
  #   "Try '--json' instead."         (cargo, gh, many others)
  #   "Use '--json' to ..."           (python/click)
  #   "Suggestion: --json"            (jj, pijul, etc.)
  #   "Maybe you meant ..."           (some Go tools)
  #   "valid options are: --json ..."  (lots of argparse)
  #   "available (flags|options): --json ..."  (cobra)
  # The original regex caught only `did you mean|use [`']?-{1,2}[a-z]`, which
  # misses every "Try"/"Suggestion"/"Maybe"/"valid" variant — those got
  # mis-classified as useless_error and the corpus reported a false negative
  # for tools that were genuinely helpful. Expand the alternation to cover
  # the patterns above; case-insensitive.
  # Extended patterns include "Use <tool> --help" (jq, many C tools), "see
  # the X manpage" (jq, git), and "for help" (common closing phrase). These
  # are weaker than `did you mean --json?` (the agent has to do another
  # round-trip to resolve), but still genuinely point the agent at where to
  # learn the fix — strictly better than useless_error.
  if [ "$exit_code" -ne 0 ] && echo "$stderr" | grep -qiE \
       'did you mean|maybe you (mean|meant)|perhaps you (mean|meant)|try [`'\'']?-{1,2}[a-z]|use [`'\'']?-{1,2}[a-z]|use [a-z][a-zA-Z0-9_-]* (--help|-h)\b|suggestion[:.]?[[:space:]]*[`'\'']?-{1,2}[a-z]|(valid|available) (flags|options|commands|subcommands)|see (the )?[a-z][a-zA-Z0-9_-]* (manpage|man page|docs|documentation)|for help with|--help for'; then
    echo "useful_hint"; return
  fi
  if [ "$exit_code" -ne 0 ]; then
    echo "useless_error"; return
  fi
  if [ "$exit_code" -eq 0 ] && echo "$stderr$stdout" | grep -qiE 'interpreting|deprecated|use --'; then
    echo "inferred_and_acted"; return
  fi
  echo "inferred_and_acted"
}

run_corpus() {
  local partial="$1"
  [ -f "$partial" ] || return 0
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    local invocation predicted
    local stderr_tmp stdout exit_code stderr classification matched skip_reason cwd
    invocation=$(echo "$line" | jq -r '.invocation // ""')
    predicted=$(echo "$line" | jq -r '.predicted_outcome // "unknown"')
    cwd=$(echo "$line" | jq -r '.cwd // ""')

    local mutates safe_to_run
    mutates=$(echo "$line" | jq -r '.mutates // false')
    safe_to_run=$(echo "$line" | jq -r '.safe_to_run // false')
    skip_reason=""
    stdout=""
    stderr=""
    exit_code=0

    local argv=()
    local argv_out argv_rc
    classification=""
    if [ "$mutates" = "true" ] && [ "$safe_to_run" != "true" ]; then
      classification="skipped"
      skip_reason="would mutate state without safe_to_run=true"
    elif [ -n "$cwd" ] && [ ! -d "$cwd" ]; then
      classification="skipped"
      skip_reason="cwd does not exist: $cwd"
    elif [ -n "$cwd" ]; then
      # Confine .cwd to a subtree under $SIBLING. The corpus JSONL is
      # produced by an LLM subagent (intent-stresser-savvy.md), and a
      # malicious or confused generator could set .cwd to a path outside
      # the audit workspace — e.g. /etc/sudoers.d, $HOME/.gnupg. The
      # runner would `cd` there and execute the target tool, which then
      # auto-discovers config files (`.git/config`, `.npmrc`,
      # `pyproject.toml`, `gh auth status` directory walk, etc.) from
      # that location, potentially leaking secrets or behaving
      # unexpectedly. Resolve the realpath and verify it's under
      # $SIBLING; reject otherwise.
      local cwd_real sibling_real
      cwd_real=$(/usr/bin/realpath -m "$cwd" 2>/dev/null || echo "$cwd")
      sibling_real=$(/usr/bin/realpath -m "$SIBLING" 2>/dev/null || echo "$SIBLING")
      case "$cwd_real" in
        "$sibling_real"|"$sibling_real"/*)
          : # OK: cwd is within sibling subtree
          ;;
        *)
          classification="skipped"
          skip_reason="cwd outside audit workspace: $cwd (must be under $SIBLING)"
          ;;
      esac
    fi
    if [ "$classification" != "skipped" ]; then
      # Capture row_to_argv's stdout AND exit code. `mapfile < <(...)` would
      # have lost the inner return code, silently treating an unsafe legacy
      # invocation as an empty argv (then running `timeout 5` with no command).
      set +e
      argv_out=$(row_to_argv "$line" "$invocation")
      argv_rc=$?
      set -e
      if [ "$argv_rc" -ne 0 ]; then
        classification="skipped"
        skip_reason="legacy invocation missing or contains shell syntax; provide argv[] instead"
      else
        mapfile -t argv <<< "$argv_out"
      fi
    fi

    if [ "$classification" != "skipped" ]; then
      local env_args=("NO_COLOR=1" "TERM=dumb" "CI=true")
      local env_kv env_key
      # Allowlist filter on .env keys. The corpus JSONL is produced by an
      # LLM subagent, and a malicious or confused generator could set
      # entries like LD_PRELOAD, PATH, PYTHONPATH, NODE_OPTIONS, GIT_*,
      # ASAN_OPTIONS, etc. — all of which the next subprocess would
      # inherit and potentially execute attacker-supplied code from. The
      # legitimate purpose of the .env field is to inject the typo'd
      # tool-specific env vars from the surface inventory (e.g.
      # `MYTOOL_HOME=1`), which conform to the `^[A-Z][A-Z0-9_]+$`
      # convention. Reject anything else with a clear log line; the
      # corpus entry is otherwise still attempted with the safe baseline
      # (NO_COLOR/TERM/CI) plus any passing env keys.
      local DENY_ENV_KEYS='^(LD_|DYLD_|GLIBC_|MALLOC_|TMP|TMPDIR|HOME|USER|UID|GID|PATH|MANPATH|LIBRARY_PATH|PYTHONPATH|PERL5LIB|RUBYLIB|NODE_PATH|NODE_OPTIONS|JAVA_TOOL_OPTIONS|SSL_CERT_|GIT_|SSH_|GPG_|SUDO_|ASAN_|TSAN_|MSAN_|UBSAN_)'
      while IFS= read -r env_kv; do
        [ -z "$env_kv" ] && continue
        env_key="${env_kv%%=*}"
        if [[ "$env_key" =~ $DENY_ENV_KEYS ]]; then
          echo "skipping unsafe env key '$env_key' from corpus entry" >&2
          continue
        fi
        if ! [[ "$env_key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
          echo "skipping malformed env key '$env_key' from corpus entry" >&2
          continue
        fi
        env_args+=("$env_kv")
      done < <(echo "$line" | jq -r '.env // {} | to_entries[] | "\(.key)=\(.value|tostring)"')

      # Run with timeout 5; stdin closed; no shell; per-call temp.
      stderr_tmp=$(mktemp /tmp/aerg_stderr.XXXXXX)
      set +e
      if [ -n "$cwd" ]; then
        stdout=$(cd "$cwd" && env "${env_args[@]}" timeout 5 "${argv[@]}" </dev/null 2>"$stderr_tmp")
      else
        stdout=$(env "${env_args[@]}" timeout 5 "${argv[@]}" </dev/null 2>"$stderr_tmp")
      fi
      exit_code=$?
      set -e
      stderr=$(cat "$stderr_tmp" 2>/dev/null || true)
      # Truncate (per AGENTS.md, no `rm`); /tmp cleanup is OS-managed.
      : > "$stderr_tmp" 2>/dev/null || true
      classification=$(classify "$exit_code" "$stdout" "$stderr")
    fi

    # Truncate stdout/stderr at 4 KB each. The IO-CONTRACTS spec and
    # intent-runner.md both require: "If truncated, suffix with
    # `... [truncated]`." Without the marker, downstream consumers (Phase 4
    # recommenders) cannot tell a partial capture apart from a tool that
    # genuinely emitted exactly 4096 bytes — and may misread truncated
    # stderr as "tool said nothing helpful here."
    if [ "${#stdout}" -gt 4096 ]; then
      stdout="${stdout:0:4096}... [truncated]"
    fi
    if [ "${#stderr}" -gt 4096 ]; then
      stderr="${stderr:0:4096}... [truncated]"
    fi

    if [ "$classification" = "$predicted" ]; then matched=true; else matched=false; fi
    local argv_json
    if [ "${#argv[@]}" -eq 0 ]; then
      # Skipped paths never populate the local argv array. Falling back to
      # an empty [] would clobber the input record's argv via the
      # `$base + {argv: $argv}` merge below, leaving the audit trail with
      # no record of WHICH invocation was skipped — a debug-impeding loss.
      # Preserve the input's argv instead (default to [] only when the input
      # also has none).
      argv_json=$(echo "$line" | jq -c '.argv // []')
    else
      argv_json=$(printf '%s\n' "${argv[@]}" | jq -R . | jq -cs .)
    fi

    jq -nc --argjson base "$line" --arg act "$classification" \
           --arg out "$stdout" --arg err "$stderr" --argjson argv "$argv_json" \
           --arg cwd "$cwd" --arg skip_reason "$skip_reason" \
           --argjson ec "$exit_code" --argjson m "$matched" '
      $base + {
        argv: $argv,
        cwd: (if $cwd == "" then null else $cwd end),
        env: ($base.env // {}),
        mutates: ($base.mutates // false),
        safe_to_run: ($base.safe_to_run // (if ($base.mutates // false) then false else true end)),
        classification: $act,
        matched_predicted: $m,
        stdout: $out,
        stderr: $err,
        exit_code: $ec,
        skip_reason: (if $skip_reason == "" then null else $skip_reason end),
        ran_at: (now | todateiso8601)
      }
    ' >> "$OUT"
  done < "$partial"
}

run_corpus "$AUDIT/partial/intent_naive.jsonl"
run_corpus "$AUDIT/partial/intent_savvy.jsonl"

# Summary
n=$(wc -l < "$OUT")
silent=$(jq -r 'select(.classification == "silent_fail") | .corpus_id' "$OUT" | wc -l)
useless=$(jq -r 'select(.classification == "useless_error") | .corpus_id' "$OUT" | wc -l)
useful=$(jq -r 'select(.classification == "useful_hint") | .corpus_id' "$OUT" | wc -l)
inferred=$(jq -r 'select(.classification == "inferred_and_acted") | .corpus_id' "$OUT" | wc -l)
skipped=$(jq -r 'select(.classification == "skipped") | .corpus_id' "$OUT" | wc -l)

cat >&2 <<EOF
intent corpus run complete: $n total entries
  silent_fail: $silent
  useless_error: $useless
  useful_hint: $useful
  inferred_and_acted: $inferred
  skipped: $skipped
EOF

exit 0
