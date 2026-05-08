#!/usr/bin/env bash
# scripts/manifest_update.sh — Atomically update audit/manifest.json.
# Helper used by phase steps to update fields without losing concurrent edits.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/manifest_update.sh <sibling> <jq-update-expression>

Atomically updates <sibling>/audit/manifest.json by applying the given jq
expression. An exclusive flock is held across the read-modify-write so two
concurrent invocations (e.g. parallel subagents updating different phase
summaries) cannot clobber each other.

Args:
  <sibling>            Audit workspace root.
  <jq-update-expr>     Any jq expression that returns the new manifest value.
                       Quote it carefully — your shell sees this first.

SECURITY — OPERATOR-ONLY TOOL.
The jq expression is executed verbatim with full jq capabilities, including
$ENV access, file reads via @json/import, and downstream-shell-out via @sh
formatting if a consumer eval's the result. **Never invoke this with a jq
expression assembled from untrusted input** (subagent output, recommendation
fields, or any data that came from an LLM). The contract is: the parent
agent constructs each expression as a known-safe literal string in the
script that calls this tool. There is no allowlist or AST filter — that
would defeat the tool's purpose, which is to let phase scripts atomically
apply arbitrary jq updates to the manifest.

Examples:
  scripts/manifest_update.sh /path/to/__audit \
    '.passes[-1].summary.surfaces_inventoried = 142'

  scripts/manifest_update.sh /path/to/__audit \
    '.current_pass = 2 | ."pass_N+1_ready" = false'

Exit codes:
  0  Success.
  1  Missing arguments (usage printed).
  2  Manifest file not found.
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
EXPR="$2"

MANIFEST="$SIBLING/audit/manifest.json"

if [ ! -f "$MANIFEST" ]; then
  echo "manifest not found: $MANIFEST" >&2
  exit 2
fi

TMP=$(mktemp "${MANIFEST}.tmp.XXXXXX")
# Use mktemp's random suffix instead of `${MANIFEST}.tmp.$$` (PID-based,
# guessable). The PID form is exposed to a same-UID symlink-race attacker
# who pre-creates `${MANIFEST}.tmp.<our-PID>` as a symlink; jq's redirect
# would then write into the symlink target. mktemp atomically creates with
# O_EXCL and 0600 in the same directory as the manifest, eliminating that
# window. Same-FS so the trailing `mv` is atomic. (Per round-J security
# review I4-#5.)

# Hold an exclusive lock for the read-modify-write so two concurrent invocations
# (e.g. parallel subagents both updating their phase summaries) don't clobber
# each other. The lock file lives next to the manifest. `flock` is required —
# without it, the read-modify-write races and silently corrupts the manifest
# under concurrent load. Fail hard rather than warn-and-race; the prior
# warn-and-fall-through path was a documented attractive nuisance per the
# round-I security review.
LOCK="${MANIFEST}.lock"
if ! command -v flock >/dev/null 2>&1; then
  echo "manifest_update.sh requires flock(1); install util-linux or block concurrent invocations another way" >&2
  exit 3
fi
exec 9>"$LOCK"
flock 9
jq "$EXPR" "$MANIFEST" > "$TMP"
mv "$TMP" "$MANIFEST"
flock -u 9
exec 9>&-

echo "manifest updated: $EXPR"
exit 0
