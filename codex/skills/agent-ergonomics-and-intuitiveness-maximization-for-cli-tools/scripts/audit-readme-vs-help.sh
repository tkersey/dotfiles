#!/usr/bin/env bash
# scripts/audit-readme-vs-help.sh — Detect drift between README's documented commands
# and the tool's actual --help. Surfaces "documentation rot" as a finding.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/audit-readme-vs-help.sh <target-repo> <tool-binary>

Detects drift between the README's mentioned `<tool> <verb>` invocations
and the tool's actual `--help` verb list. Emits a JSON object listing
verbs in the README but absent from --help (potentially obsolete) and
verbs in --help but absent from the README (potentially undocumented).

Args:
  <target-repo>   Path to the target repo containing README.md (or README).
  <tool-binary>   Path to the CLI binary; basename (with .sh stripped) is
                  the prefix searched for in the README.

Output:
  Single JSON object on stdout. drift_score is the count of mismatches.

Exit codes:
  0  Success.
  1  Missing arguments (usage printed).
  2  Target dir not found, or no README found in target.

Example:
  scripts/audit-readme-vs-help.sh ~/code/mytool ~/code/mytool/target/release/mytool
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

TARGET="$1"
TOOL="$2"

if [ ! -d "$TARGET" ]; then
  echo "target not a directory: $TARGET" >&2
  exit 2
fi

readme="$TARGET/README.md"
[ ! -f "$readme" ] && readme="$TARGET/README"
[ ! -f "$readme" ] && { echo "no README found in $TARGET" >&2; exit 2; }

# Extract commands mentioned in README (heuristic: code blocks containing the tool name).
# Just the verb (first word after the tool name); flags are handled separately.
#
# `tool_basename` strips the `.sh` extension so a bash CLI named `mytool.sh` matches
# README mentions of `mytool` (most authors omit the `.sh` in docs).
#
# Under pipefail, `grep` returning no matches (exit 1) would propagate and kill
# the script via set -e, even though "no commands found in README" is a perfectly
# valid outcome. Wrap the grep so an empty result is treated as a clean zero.
tool_basename=$(basename "$TOOL")
tool_basename="${tool_basename%.sh}"
readme_commands=$({ grep -oE "${tool_basename}[[:space:]]+[a-z][a-z0-9_-]+" "$readme" 2>/dev/null || true; } \
  | awk '{print $2}' | sort -u | head -20)

# Extract verbs from --help
help_out=$(timeout 5 "$TOOL" --help 2>&1 || true)
help_verbs=$(echo "$help_out" | awk '
  /^[Cc]ommands:|^[Ss]ubcommands:/ { in_cmds=1; next }
  /^[A-Z]/ && in_cmds { in_cmds=0 }
  in_cmds && /^  [a-z][a-zA-Z0-9_-]+/ { print $1 }
' | sort -u)

# Find README commands not in --help (potentially obsolete)
not_in_help=()
while IFS= read -r line; do
  [ -z "$line" ] && continue
  verb=$(echo "$line" | awk '{print $1}')
  if ! echo "$help_verbs" | grep -qx "$verb"; then
    not_in_help+=("$verb")
  fi
done <<< "$readme_commands"

# Find --help verbs not in README (potentially undocumented).
# Use [[:space:]] (POSIX) instead of `\s` (Perl-only; not portable across grep
# implementations). The trailing boundary uses a negated word-char class so the
# verb must end at a non-identifier character — including backticks (common in
# `\`foo verb\`` inline code), punctuation, or end of line.
not_in_readme=()
while IFS= read -r verb; do
  [ -z "$verb" ] && continue
  if ! grep -qE "${tool_basename}[[:space:]]+${verb}([^a-zA-Z0-9_-]|\$)" "$readme"; then
    not_in_readme+=("$verb")
  fi
done <<< "$help_verbs"

# Build arrays as JSON via jq (handles tool names / paths / verbs containing
# `"` or `\` correctly, instead of raw-interpolating into a JSON template).
if [ ${#not_in_help[@]} -eq 0 ]; then
  OBSOLETE_JSON='[]'
else
  OBSOLETE_JSON=$(printf '%s\n' "${not_in_help[@]}" | jq -R . | jq -cs .)
fi
if [ ${#not_in_readme[@]} -eq 0 ]; then
  UNDOC_JSON='[]'
else
  UNDOC_JSON=$(printf '%s\n' "${not_in_readme[@]}" | jq -R . | jq -cs .)
fi
README_CMDS_JSON=$(printf '%s' "$readme_commands" | jq -Rs 'split("\n") | map(select(length > 0))')
HELP_VERBS_JSON=$(printf '%s' "$help_verbs" | jq -Rs 'split("\n") | map(select(length > 0))')

jq -n \
  --arg tool "$tool_basename" \
  --arg readme_path "$readme" \
  --argjson readme_commands_mentioned "$README_CMDS_JSON" \
  --argjson help_verbs "$HELP_VERBS_JSON" \
  --argjson potentially_obsolete_in_readme "$OBSOLETE_JSON" \
  --argjson undocumented_verbs "$UNDOC_JSON" \
  --argjson drift_score "$((${#not_in_help[@]} + ${#not_in_readme[@]}))" \
  '{
    tool: $tool,
    readme_path: $readme_path,
    readme_commands_mentioned: $readme_commands_mentioned,
    help_verbs: $help_verbs,
    potentially_obsolete_in_readme: $potentially_obsolete_in_readme,
    undocumented_verbs: $undocumented_verbs,
    drift_score: $drift_score
  }'
