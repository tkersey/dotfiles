#!/usr/bin/env bash
# scripts/inventory_surfaces.sh — Recursive --help walk for one tool.
# Emits a JSONL skeleton of surfaces (verbs + flags) discovered at runtime.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/inventory_surfaces.sh <tool-binary> [--depth N | --depth=N]

Recursively walks <tool-binary>'s --help output and emits a JSONL skeleton
(one record per line) of every discovered subcommand and flag.

Args:
  <tool-binary>   Path or PATH-resolvable name of the CLI to inventory.
                  Must already be executable (this script does not build).
  --depth N       Max recursion depth into nested subcommands. Default: 999.
                  Both `--depth N` (space) and `--depth=N` (equals) forms accepted.

Output:
  JSONL records to stdout — one per surface (verb + flag). Diagnostics on
  stderr. Use as a starting point for audit/surface_inventory.jsonl; the
  surface-inventorist subagent then augments with source-derived surfaces.

Examples:
  scripts/inventory_surfaces.sh /usr/bin/gh > audit/surface_inventory.jsonl
  scripts/inventory_surfaces.sh ./target/release/mytool --depth 3
  scripts/inventory_surfaces.sh ./target/release/mytool --depth=999

Exit codes:
  0  Success.
  1  Missing or invalid arguments (this usage message printed).
  2  Tool not found or not executable.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

TOOL="$1"
shift

validate_depth() {
  if [ -z "$DEPTH" ] || ! [[ "$DEPTH" =~ ^[0-9]+$ ]]; then
    echo "--depth requires a non-empty numeric value (got '$DEPTH')" >&2
    echo "(run with --help for usage)" >&2
    exit 2
  fi
}

DEPTH=999
case "${1:-}" in
  --depth)
    # `--depth N` form (space-separated). Reject `--depth` with no value rather
    # than silently using the default — an unconsumed `--depth` would have been
    # a typo for the user. (Without this check, `shift 2` with only one
    # positional left fails under set -e and the script exits 1 with no stderr
    # message.)
    if [ -z "${2:-}" ]; then
      echo "--depth requires a numeric argument" >&2
      echo "(run with --help for usage)" >&2
      exit 2
    fi
    DEPTH="$2"
    validate_depth
    shift 2
    ;;
  --depth=*)
    # `--depth=N` form (equals-separated; documented in TROUBLESHOOTING.md).
    DEPTH="${1#--depth=}"
    validate_depth
    shift
    ;;
  "") ;;
  *)
    echo "unexpected argument: $1" >&2
    echo "(run with --help for usage)" >&2
    exit 2
    ;;
esac

if [ "$#" -gt 0 ]; then
  echo "unexpected extra argument: $1" >&2
  echo "(run with --help for usage)" >&2
  exit 2
fi

if ! command -v "$TOOL" >/dev/null 2>&1 && [ ! -x "$TOOL" ]; then
  echo "tool not found / not executable: $TOOL" >&2
  exit 2
fi

# Capture top-level help and preserve the real exit code. A tool whose
# `--help` exits nonzero is itself an ergonomics finding; don't record it as
# exit_code=0 in the surface inventory.
set +e
TOP_HELP=$(timeout 5 "$TOOL" --help 2>&1)
TOP_RC=$?
set -e

# Emit verb surface for the top-level binary itself
TOOL_NAME=$(basename "$TOOL")
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
surface_segment() {
  local raw="$1"
  local clean
  clean=$(printf '%s' "$raw" \
    | LC_ALL=C tr -c 'A-Za-z0-9._-' '_' \
    | sed -E 's/^[^A-Za-z0-9]+//; s/_+/_/g; s/_$//')
  if [ -z "$clean" ]; then
    clean="x$(printf '%s' "$raw" | sha256sum | cut -c1-8)"
  elif [ "$clean" != "$raw" ]; then
    clean="${clean}_h$(printf '%s' "$raw" | sha256sum | cut -c1-8)"
  fi
  printf '%s' "$clean"
}

json_string() {
  jq -Rn --arg value "$1" '$value'
}

TOOL_ID=$(surface_segment "$TOOL_NAME")
TOOL_NAME_JSON=$(json_string "$TOOL_NAME")
TOOL_HELP_INVOCATION_JSON=$(json_string "$TOOL_NAME --help")
printf '{"surface_id":"verb__%s","subtree":null,"kind":"verb","name":%s,"source":{"file":null,"line":null},"runtime":{"help_excerpt":%s,"invocation":%s,"exit_code":%d},"description":"top-level binary","required":false,"deprecated":false,"mutates":null,"discovered_at":"%s"}\n' \
  "$TOOL_ID" "$TOOL_NAME_JSON" \
  "$(printf '%s\n' "$TOP_HELP" | sed -n '1,3p' | jq -Rs .)" \
  "$TOOL_HELP_INVOCATION_JSON" \
  "$TOP_RC" \
  "$NOW"

# Helper: extract flag definitions from a help blob.
# Under `set -euo pipefail`, when grep finds no matches (a tool with no flags) it
# exits 1, which propagates through pipefail and would otherwise terminate the
# whole script before subcommand walking. Swallow the no-match case explicitly.
extract_flags() {
  local help_blob="$1"
  # First admit only option-table-looking lines, then pre-split on `,` `|` `/`
  # so each flag token lands on its own line. Help
  # formats commonly use those characters as separators between short and
  # long forms — e.g. `  -n, --null-input`, `  -c|--compact`, `  -r/--raw`.
  # The previous one-shot regex required either `^[[:space:]]+` or `, ` to
  # precede each match. After capturing `-n` and consuming the trailing `,`,
  # the position before `--null-input` had only a single mid-line space, so
  # the long form was silently dropped — the inventory was missing half of
  # every dual-form flag definition. Tokenizing before the final flag match
  # lets every form be matched. Scanning the option field from each admitted
  # line also catches dense GNU find-style rows such as
  # "-depth -files0-from FILE -maxdepth LEVELS".
  #
  # Keep that anchor bounded. Some CLIs document embedded mini-languages in
  # help text; a deeply indented prose continuation such as "              -max
  # places..." is not a command-line option and must not become a surface.
  { echo "$help_blob" \
      | awk '
          /^[[:space:]]{0,8}-/ {
            line = $0
            sub(/[[:space:]][[:space:]][[:space:]]+[^[:space:]-].*$/, "", line)
            print line
          }
        ' \
      | tr ',|/' '   ' \
      | awk '{ for (i = 1; i <= NF; i++) print $i }' \
      | grep -oE '^(--[a-zA-Z][a-zA-Z0-9_-]*|-[a-zA-Z][a-zA-Z0-9_-]*)' \
      || true; } \
    | sort -u
}
# Regex breakdown:
#   - Line admission: column 0 through 8 spaces before a dash. Some CLIs
#     (ffmpeg, X11, Java -X*) print flags at column 0 without indent — the
#     previous regex required leading whitespace and missed every such flag.
#     Very deep indents are usually wrapped prose, not option tables.
#   - Option-field trim: stop before a wide whitespace gap followed by prose,
#     so descriptions like "use -x for debug" do not become surfaces.
#   - Tokenization: split separators and whitespace before matching, so several
#     space-separated flags on one admitted line are each captured instead of
#     every other flag being skipped by a consumed delimiter.
#   - Flag shape: `--name` (double-dash long, GNU style) OR `-name` /
#     `-x` (single-dash long like `-version` / `-muxers` from ffmpeg-style
#     CLIs, or single-char short like `-h`). The previous `-[a-zA-Z]` form
#     only captured single-char short flags, missing the entire single-dash-
#     long family.
#   - Trailing option syntax such as `--color[=WHEN]` and `--flag=VALUE` is
#     naturally trimmed by the token-level prefix match.

# Emit top-level (global) flag surfaces
extract_flags "$TOP_HELP" | while read -r flag; do
  [ -z "$flag" ] && continue
  flag_clean=$(echo "$flag" | sed -E 's/^-+//')
  [ -z "$flag_clean" ] && continue
  if [[ "$flag" == --* ]]; then
    flag_name="--$flag_clean"
  else
    flag_name="-$flag_clean"
  fi
  flag_id=$(surface_segment "$flag_clean")
  flag_name_json=$(json_string "$flag_name")
  # `type` and `enum_values` are in IO-CONTRACTS § flag schema but cannot be
  # determined from --help alone; emit null and let the surface-inventorist
  # subagent fill them in from source-level evidence.
  printf '{"surface_id":"flag__global__%s","subtree":null,"kind":"flag","name":%s,"short":null,"type":null,"enum_values":null,"source":{"file":null,"line":null},"runtime":{"help_excerpt":null,"invocation":%s,"exit_code":0},"description":null,"required":false,"deprecated":false,"discovered_at":"%s"}\n' \
    "$flag_id" "$flag_name_json" "$TOOL_HELP_INVOCATION_JSON" "$NOW"
done

# Try to extract subcommand list from --help (best-effort; framework-dependent)
# Common patterns:
#   "  list   List items"
#   "Commands:\n  list ..."
#
# SECURITY: subcommand names are later split into an argv array to allow
# multi-level paths like "auth login". A subcommand name with shell metachars
# (`;`, `&`, backticks, `$()`) would be a command-injection vector. Filter to
# the conservative `[a-zA-Z][a-zA-Z0-9_-]*` shape and skip anything else.
SUBCMDS=$(echo "$TOP_HELP" | awk '
  # Section headers come in many flavors. clap/argparse: "Commands:" /
  # "Subcommands:" / "SUBCOMMANDS:". Cobra (gh, kubectl, helm): all-caps
  # multi-section, e.g. "CORE COMMANDS" / "ADDITIONAL COMMANDS". Git: prose
  # section headers like "start a working area (see also: git help tutorial)"
  # for `git --help`, plus Title-Case "Main Porcelain Commands" /
  # "Low-level Commands" for `git help -a`. Without git-style coverage
  # the inventory captured 0 subcommands for git despite its 100+ verbs.
  /^[Cc]ommands:?$/                                  { in_cmds=1; next }
  /^[Ss]ubcommands:?$/                               { in_cmds=1; next }
  /^SUBCOMMANDS:?$/                                  { in_cmds=1; next }
  /^[A-Z][A-Z ]* (COMMANDS|SUBCOMMANDS):?[[:space:]]*$/       { in_cmds=1; next }
  /^[A-Z][A-Za-z ]*[Cc]ommands:?[[:space:]]*$/                { in_cmds=1; next }   # "Main Porcelain Commands" / "All commands:" (npm)
  /\(see also: .*help.*\)[[:space:]]*$/                       { in_cmds=1; next }   # git "(see also: git help X)"
  /^These are .*[Cc]ommands.*:[[:space:]]*$/                  { in_cmds=1; next }   # "These are common Git commands ...:"
  # End of section: a non-indented line that is NOT itself a commands
  # header. Indented lines (entries) and blank lines stay in_cmds. Without
  # negation, the next "FOO COMMANDS" header would close in_cmds before its
  # own opening rule could fire.
  /^[A-Za-z]/ && in_cmds \
    && !/[Cc]ommands:?[[:space:]]*$/ \
    && !/SUBCOMMANDS:?[[:space:]]*$/ \
    && !/\(see also: .*help.*\)[[:space:]]*$/ { in_cmds=0 }
  in_cmds && /^[[:space:]][[:space:]]+[a-z][a-zA-Z0-9_-]*/ {
    # Most CLIs use one subcommand per line ("auth:    Authenticate ..." —
    # cobra/git/clap). npm uses a comma-separated wall ("    access,
    # adduser, audit, bugs, ..."). Distinguish by comma count: if the line
    # has 2+ commas, treat as a comma-list and split; otherwise just
    # take $1 (the first whitespace-token). Without this gate, splitting
    # by /[ \t,]+/ on "auth:    Authenticate gh and git" emits "auth",
    # "Authenticate" (rejected by post-grep), "gh", "and", "git" — bogus
    # verbs that the walker then tries to recurse into, multiplying the
    # inventory size and dropping real commands.
    comma_count = gsub(/,/, ",", $0)
    if (comma_count >= 2) {
      n = split($0, tokens, /[ \t,]+/)
      for (i = 1; i <= n; i++) {
        name = tokens[i]
        if (name == "") continue
        sub(/:$/, "", name)
        sub(/\*$/, "", name)
        print name
      }
    } else {
      name = $1
      sub(/:$/, "", name)   # cobra "auth:"
      sub(/,$/, "", name)   # trailing comma if 1-comma line (rare)
      sub(/\*$/, "", name)  # docker "compose*" external plugin marker
      print name
    }
  }
' | grep -E '^[a-z][a-z0-9_-]*$' || true)

# Walk subcommands recursively (depth-bounded)
walk() {
  local cmd_path="$1"
  local depth="$2"
  [ "$depth" -le 0 ] && return

  local sub_help
  local cmd_args=()
  read -r -a cmd_args <<< "$cmd_path"
  local sub_rc
  set +e
  sub_help=$(timeout 5 "$TOOL" "${cmd_args[@]}" --help 2>&1)
  sub_rc=$?
  set -e
  local sub_name="${cmd_path##* }"
  local cmd_id
  cmd_id=$(surface_segment "$cmd_path")
  local cmd_path_json
  local sub_name_json
  local sub_invocation_json
  cmd_path_json=$(json_string "$cmd_path")
  sub_name_json=$(json_string "$sub_name")
  sub_invocation_json=$(json_string "$TOOL_NAME $cmd_path --help")

  # Emit verb surface for this subcommand
  printf '{"surface_id":"verb__%s","subtree":%s,"kind":"verb","name":%s,"source":{"file":null,"line":null},"runtime":{"help_excerpt":%s,"invocation":%s,"exit_code":%d},"description":null,"required":false,"deprecated":false,"mutates":null,"discovered_at":"%s"}\n' \
    "$cmd_id" \
    "$cmd_path_json" \
    "$sub_name_json" \
    "$(printf '%s\n' "$sub_help" | sed -n '1,3p' | jq -Rs .)" \
    "$sub_invocation_json" \
    "$sub_rc" \
    "$NOW"

  # Extract flags from this subcommand's help.
  extract_flags "$sub_help" | while read -r flag; do
    [ -z "$flag" ] && continue
    flag_clean=$(echo "$flag" | sed -E 's/^-+//')
    [ -z "$flag_clean" ] && continue
    if [[ "$flag" == --* ]]; then
      flag_name="--$flag_clean"
    else
      flag_name="-$flag_clean"
    fi
    flag_id=$(surface_segment "$flag_clean")
    flag_name_json=$(json_string "$flag_name")
    # `type` + `enum_values` are nulled here for the same reason as the global
    # flags above; subagent fills them in from source.
    printf '{"surface_id":"flag__%s__%s","subtree":%s,"kind":"flag","name":%s,"short":null,"type":null,"enum_values":null,"source":{"file":null,"line":null},"runtime":{"help_excerpt":null,"invocation":%s,"exit_code":0},"description":null,"required":false,"deprecated":false,"discovered_at":"%s"}\n' \
      "$cmd_id" "$flag_id" \
      "$cmd_path_json" \
      "$flag_name_json" \
      "$sub_invocation_json" \
      "$NOW"
  done

  # Recurse into nested subcommands.
  # SECURITY: same name-shape filter as the top level — `$cmd_path` is later
  # split into an argv array, so a metachar in `$n` must never enter the path.
  local nested
  nested=$(echo "$sub_help" | awk '
    # Same broadened section-header regex as top-level: clap/argparse,
    # cobra/gh-style ALL-CAPS, Title-Case "Main Porcelain Commands", and
    # git-style "(see also: git help X)" prose headers.
    /^[Cc]ommands:?$/                                { in_cmds=1; next }
    /^[Ss]ubcommands:?$/                             { in_cmds=1; next }
    /^SUBCOMMANDS:?$/                                { in_cmds=1; next }
    /^[A-Z][A-Z ]* (COMMANDS|SUBCOMMANDS):?[[:space:]]*$/     { in_cmds=1; next }
    /^[A-Z][A-Za-z ]*[Cc]ommands:?[[:space:]]*$/              { in_cmds=1; next }
    /\(see also: .*help.*\)[[:space:]]*$/                     { in_cmds=1; next }
    /^These are .*[Cc]ommands.*:[[:space:]]*$/                { in_cmds=1; next }
    /^[A-Za-z]/ && in_cmds \
      && !/[Cc]ommands:?[[:space:]]*$/ \
      && !/SUBCOMMANDS:?[[:space:]]*$/ \
      && !/\(see also: .*help.*\)[[:space:]]*$/ { in_cmds=0 }
    in_cmds && /^[[:space:]][[:space:]]+[a-z][a-zA-Z0-9_-]*/ {
      comma_count = gsub(/,/, ",", $0)
      if (comma_count >= 2) {
        n = split($0, tokens, /[ \t,]+/)
        for (i = 1; i <= n; i++) {
          name = tokens[i]
          if (name == "") continue
          sub(/:$/, "", name)
          sub(/\*$/, "", name)
          print name
        }
      } else {
        name = $1
        sub(/:$/, "", name)
        sub(/,$/, "", name)
        sub(/\*$/, "", name)
        print name
      }
    }
  ' | grep -E '^[a-z][a-z0-9_-]*$' || true)
  for n in $nested; do
    walk "$cmd_path $n" $((depth - 1))
  done
}

for sub in $SUBCMDS; do
  walk "$sub" "$DEPTH"
done

exit 0
