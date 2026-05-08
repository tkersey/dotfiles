#!/usr/bin/env bash
# scripts/generate_intent_corpus.sh — Phase 3 corpus generator (deterministic categories).
#
# Reads <SIBLING>/audit/surface_inventory.jsonl and algorithmically generates
# the deterministic naive-corpus categories defined in INTENT-CORPUS-GENERATION.md:
#
#   A — flag-name typos (edit-distance 1)
#   C — spelling variants (US/UK, plural/singular, synonym pairs)
#   D — tool-family confusion (ls/list, rm/delete, etc.)
#   G — env-var prefix typos
#
# These categories are pure mechanical generation — no LLM needed. The boundary
# cases (intent-stresser-savvy: H/I/J/K/L/M) still require source-aware LLM
# judgment; the script prints the spawn instructions for those at the end.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/generate_intent_corpus.sh <sibling> [--tool <tool-name>]

Generates deterministic naive-corpus entries (categories A/C/D/G per
INTENT-CORPUS-GENERATION.md) into <sibling>/audit/partial/intent_naive.jsonl
by reading <sibling>/audit/surface_inventory.jsonl. Then prints the spawn
instruction for the savvy subagent (which still needs LLM judgment).

Args:
  <sibling>      Audit workspace root.
  --tool NAME    Tool basename to use as argv[0] in generated entries.
                 Defaults to the first binary listed in
                 <sibling>/audit/phase0_cli.json (or "tool" if absent).

Output:
  Generates <sibling>/audit/partial/intent_naive.jsonl (overwrite). Prints
  the per-category counts + the savvy spawn instruction to stdout.

Exit codes:
  0  Success (corpus generated; savvy spawn instruction printed).
  1  Missing arguments.
  2  surface_inventory.jsonl not found (run inventory_surfaces.sh + the
     surface-inventorist subagent first).

Example:
  scripts/generate_intent_corpus.sh /path/to/__audit --tool mytool
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

SIBLING="$1"
shift

TOOL_NAME=""
if [ "${1:-}" = "--tool" ]; then
  if [ -z "${2:-}" ]; then
    echo "--tool requires a non-empty tool name" >&2
    usage >&2
    exit 1
  fi
  TOOL_NAME="${2:-}"
  shift 2
fi
if [ "$#" -gt 0 ]; then
  echo "unexpected argument: $1" >&2
  usage >&2
  exit 1
fi

INV="$SIBLING/audit/surface_inventory.jsonl"
if [ ! -f "$INV" ]; then
  echo "surface_inventory.jsonl not found at $INV" >&2
  echo "(run scripts/inventory_surfaces.sh and the surface-inventorist subagent first)" >&2
  exit 2
fi

if [ -z "$TOOL_NAME" ]; then
  if [ -f "$SIBLING/audit/phase0_cli.json" ]; then
    TOOL_NAME=$(jq -r '.binaries[0] // "tool"' "$SIBLING/audit/phase0_cli.json")
  else
    TOOL_NAME="tool"
  fi
fi

mkdir -p "$SIBLING/audit/partial"
OUT="$SIBLING/audit/partial/intent_naive.jsonl"
: > "$OUT"

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
counter=0
emit() {
  # Args: category predicted surface_id reason mutates safe_to_run env_json argv_token1 [argv_token2 ...]
  # Builds the argv JSON array from the trailing positional args via jq's
  # --args, so values with quotes/backslashes/whitespace don't corrupt the
  # JSON (no shell-string interpolation into a JSON literal). env_json must
  # be a valid JSON object (use '{}' for none); it lands in the env field
  # that scripts/run_intent_corpus.sh injects into the subprocess.
  #
  # mutates / safe_to_run are per-call: a destructive alias like `[tool, rm]`
  # MUST emit mutates=true + safe_to_run=false so run_intent_corpus.sh skips
  # execution (only the documented intent + classification stays in the
  # output). Hardcoding mutates:false here would let the runner happily
  # execute potentially-destructive verbs in the target tool.
  local cat="$1" pred="$2" sid="$3" reason="$4" mutates="$5" safe_to_run="$6" env_json="$7"
  shift 7
  counter=$((counter + 1))
  local cid
  cid=$(printf 'naive-%03d' "$counter")
  # `--args` enables $ARGS.positional, but jq still flag-parses the trailing
  # tokens until it sees `--`. Without the `--` separator, a positional like
  # `--no-color` (a perfectly normal CLI flag, exactly the kind of token we
  # need to inject) is rejected as `Unknown option`. Order: jq flags →
  # filter → `--args --` → positional tokens.
  jq -nc \
    --arg cid "$cid" \
    --arg cat "$cat" \
    --arg pred "$pred" \
    --arg sid "$sid" \
    --arg reason "$reason" \
    --argjson mutates "$mutates" \
    --argjson safe_to_run "$safe_to_run" \
    --argjson env "$env_json" \
    --arg now "$NOW" \
    '{
       corpus_id: $cid,
       generator: "naive",
       category: $cat,
       argv: $ARGS.positional,
       invocation: ($ARGS.positional | join(" ")),
       cwd: null,
       env: $env,
       mutates: $mutates,
       safe_to_run: $safe_to_run,
       predicted_outcome: $pred,
       stresses_surface_id: $sid,
       reason: $reason,
       generated_at: $now
     }' \
    --args -- "$@" >> "$OUT"
}

# ---- Category A: flag-name typos (edit-distance 1) ----
# For each `flag` surface, produce 3 typo variants: drop-a-letter,
# transpose-two-adjacent, and a known-typo-table fallback for short names.
typo_variants() {
  local s="$1"  # the flag-name without leading dashes
  local n=${#s}
  local out=()
  # Drop-a-letter: skip the middle char (don't drop first/last alone — too obvious)
  if [ "$n" -ge 4 ]; then
    local mid=$((n / 2))
    out+=("${s:0:mid}${s:$((mid+1))}")
  fi
  # Transpose-two-adjacent at position max(0, len/3)
  if [ "$n" -ge 3 ]; then
    local p=$((n / 3))
    local before="${s:0:p}"
    local pair="${s:p:2}"
    local rest="${s:$((p+2))}"
    if [ ${#pair} -eq 2 ]; then
      local swapped="${pair:1:1}${pair:0:1}"
      out+=("${before}${swapped}${rest}")
    fi
  fi
  # Known-typo table for very common cases
  case "$s" in
    json) out+=("jsno" "jaon" "jsonn") ;;
    color) out+=("colour" "colur") ;;
    quiet) out+=("qiet" "quite") ;;
    verbose) out+=("vebose" "verbos") ;;
    output) out+=("ouput" "outupt") ;;
    help) out+=("hlep" "halp") ;;
  esac
  printf '%s\n' "${out[@]}" | sort -u
}

flag_count=0
while IFS= read -r row; do
  [ -z "$row" ] && continue
  kind=$(echo "$row" | jq -r '.kind // ""')
  [ "$kind" = "flag" ] || continue
  name=$(echo "$row" | jq -r '.name // ""')
  sid=$(echo "$row" | jq -r '.surface_id // ""')
  # Only --long flags (skip -x short flags; too noisy)
  case "$name" in --*) ;; *) continue ;; esac
  base="${name#--}"
  # Skip very short flags (1 char) and pathological ones
  [ ${#base} -lt 2 ] && continue
  flag_count=$((flag_count + 1))
  while IFS= read -r typo; do
    [ -z "$typo" ] || [ "$typo" = "$base" ] && continue
    # No verb in argv → tool prints help/usage; non-mutating, safe to run.
    emit "A" "useful_hint" "$sid" "edit-distance-1 typo of --$base" \
      false true '{}' \
      "$TOOL_NAME" "--$typo"
  done < <(typo_variants "$base")
done < "$INV"

# ---- Category C: spelling variants (US/UK, plural/singular, synonyms) ----
# Static pairs that come up across CLIs.
declare -A C_PAIRS=(
  [color]=colour [colour]=color
  [behavior]=behaviour [behaviour]=behavior
  [organize]=organise [organise]=organize
  [license]=licence [licence]=license
  [quiet]=silent  [silent]=quiet
  [name]=label    [label]=name
)
while IFS= read -r row; do
  [ -z "$row" ] && continue
  kind=$(echo "$row" | jq -r '.kind // ""')
  [ "$kind" = "flag" ] || continue
  name=$(echo "$row" | jq -r '.name // ""')
  sid=$(echo "$row" | jq -r '.surface_id // ""')
  case "$name" in --*) ;; *) continue ;; esac
  base="${name#--}"
  variant="${C_PAIRS[$base]:-}"
  [ -z "$variant" ] && continue
  # No verb in argv → tool prints help/usage; non-mutating, safe to run.
  emit "C" "useful_hint" "$sid" \
    "spelling variant: --$base (canonical) vs --$variant (variant)" \
    false true '{}' \
    "$TOOL_NAME" "--$variant"
done < "$INV"

# ---- Category D: tool-family confusion on top-level verbs ----
# For each verb surface, try the common alias from another tool family.
declare -A D_FAMILY=(
  [list]=ls       [ls]=list
  [delete]=rm     [rm]=delete    [remove]=rm
  [move]=mv       [mv]=move      [rename]=mv
  [copy]=cp       [cp]=copy      [clone]=cp
  [create]=new    [new]=create   [add]=create
)
# Collect known verb names to avoid generating an entry that equals an existing one
known_verbs=$(jq -r 'select(.kind == "verb" and .subtree != null) | .name' "$INV" | sort -u)
while IFS= read -r row; do
  [ -z "$row" ] && continue
  kind=$(echo "$row" | jq -r '.kind // ""')
  [ "$kind" = "verb" ] || continue
  subtree=$(echo "$row" | jq -r '.subtree // ""')
  # Only top-level verbs (no nested path)
  case "$subtree" in *' '*) continue ;; esac
  name=$(echo "$row" | jq -r '.name // ""')
  sid=$(echo "$row" | jq -r '.surface_id // ""')
  alias="${D_FAMILY[$name]:-}"
  [ -z "$alias" ] && continue
  # Skip if alias is also a real verb (would just succeed)
  if echo "$known_verbs" | grep -qx "$alias"; then continue; fi
  # If either the source verb or generated alias is destructive or state-
  # creating, the target tool could mutate state should it accept the alias as
  # an undocumented synonym. Mark mutates=true and safe_to_run=false so
  # run_intent_corpus.sh classifies the entry as `skipped` instead of
  # executing it. The reason still documents the intent, so the audit trail
  # captures the agent's likely-confusion.
  is_mutating=false
  case "$name:$alias" in
    *:delete|*:remove|*:rm|*:move|*:mv|*:rename|*:copy|*:cp|*:clone|*:create|*:new|*:add|*:init|*:drop|*:destroy|*:kill|*:reset|*:purge|*:prune|*:clean|*:wipe|\
    delete:*|remove:*|rm:*|move:*|mv:*|rename:*|copy:*|cp:*|clone:*|create:*|new:*|add:*|init:*|drop:*|destroy:*|kill:*|reset:*|purge:*|prune:*|clean:*|wipe:*)
      is_mutating=true ;;
  esac
  if [ "$is_mutating" = "true" ]; then
    emit "D" "skipped" "$sid" \
      "tool-family alias: agent might try '$alias' (other-tool idiom) instead of mutating '$name' — runner will skip (mutates+!safe_to_run)" \
      true false '{}' \
      "$TOOL_NAME" "$alias"
  else
    emit "D" "useful_hint" "$sid" \
      "tool-family alias: agent might try '$alias' (other-tool idiom) instead of '$name'" \
      false true '{}' \
      "$TOOL_NAME" "$alias"
  fi
done < "$INV"

# ---- Category G: env-var prefix typos ----
# For each env surface with a known prefix, generate several typo variants.
is_runner_denylisted_env_key() {
	local key="$1"
	[[ "$key" =~ ^(LD_|DYLD_|GLIBC_|MALLOC_|TMP|TMPDIR|HOME|USER|UID|GID|PATH|MANPATH|LIBRARY_PATH|PYTHONPATH|PERL5LIB|RUBYLIB|NODE_PATH|NODE_OPTIONS|JAVA_TOOL_OPTIONS|SSL_CERT_|GIT_|SSH_|GPG_|SUDO_|ASAN_|TSAN_|MSAN_|UBSAN_) ]]
}

while IFS= read -r row; do
  [ -z "$row" ] && continue
  kind=$(echo "$row" | jq -r '.kind // ""')
  [ "$kind" = "env" ] || continue
  name=$(echo "$row" | jq -r '.name // ""')
  sid=$(echo "$row" | jq -r '.surface_id // ""')
  # Generate plausible mistakes in the env var name itself. The typo belongs in
  # the row's `env` object; otherwise the runner invokes the tool normally and
  # the corpus entry never exercises the env-var surface it claims to stress.
  prefix="${name%%_*}"
  rest="${name#"$prefix"}"
  suffix="${rest#_}"
  [ ${#prefix} -lt 4 ] && continue
  # argv is `[tool, --version]` — universally non-mutating across CLIs, so
  # mutates=false / safe_to_run=true. The injected typo'd env var is a
  # config-name perturbation (placeholder value "1"); the runner just lets
  # the tool report what it sees.
	# Drop the prefix entirely: MYTOOL_HOME -> HOME.
	if [ -n "$suffix" ] && [ "$suffix" != "$name" ]; then
		if ! is_runner_denylisted_env_key "$suffix"; then
			env_payload=$(jq -nc --arg k "$suffix" '{($k): "1"}')
			emit "G" "useless_error" "$sid" \
				"env-var prefix dropped: ${suffix} (instead of ${name})" \
				false true "$env_payload" \
				"$TOOL_NAME" "--version"
		fi
	fi
  # Transpose at position 1 (first two chars after the leading char).
  swapped_prefix="${prefix:0:1}${prefix:2:1}${prefix:1:1}${prefix:3}"
  env_payload=$(jq -nc --arg k "${swapped_prefix}${rest}" '{($k): "1"}')
  emit "G" "useless_error" "$sid" \
    "env-var prefix typo: ${swapped_prefix}${rest} (instead of ${name})" \
    false true "$env_payload" \
    "$TOOL_NAME" "--version"
  # Wrong case: MYTOOL_HOME -> mytool_home.
  lower_name="${name,,}"
  if [ "$lower_name" != "$name" ]; then
    env_payload=$(jq -nc --arg k "$lower_name" '{($k): "1"}')
    emit "G" "useless_error" "$sid" \
      "env-var wrong case: ${lower_name} (instead of ${name})" \
      false true "$env_payload" \
      "$TOOL_NAME" "--version"
  fi
done < "$INV"

# ---- Per-category counts ----
A_count=$(jq -r 'select(.category == "A") | .corpus_id' "$OUT" | wc -l)
C_count=$(jq -r 'select(.category == "C") | .corpus_id' "$OUT" | wc -l)
D_count=$(jq -r 'select(.category == "D") | .corpus_id' "$OUT" | wc -l)
G_count=$(jq -r 'select(.category == "G") | .corpus_id' "$OUT" | wc -l)

cat <<EOF
naive corpus generated: $counter entries
  A (typos):              $A_count
  C (spelling variants):  $C_count
  D (family confusion):   $D_count
  G (env-var typos):      $G_count
written: $OUT

The naive categories above are deterministic — no LLM needed. To complete
Phase 3, also spawn:

  subagents/intent-stresser-savvy.md
    Output: $SIBLING/audit/partial/intent_savvy.jsonl

The savvy generator covers boundary cases (categories H–M) that require
source-level evidence (cited file:line). After both partials exist, run:

  scripts/run_intent_corpus.sh $SIBLING <tool-binary>
EOF

exit 0
