#!/usr/bin/env bash
# tools/flip_applied.sh — Flip a recommendation to applied:true in audit/recommendations.jsonl.
#
# Sets applied=true, applied_at=now (ISO-8601), and (optionally) applied_commit_sha.
# Acquires an exclusive flock so two parallel appliers can't clobber each other's
# updates to the same JSONL file.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/flip_applied.sh <RECOMMENDATION_ID> [<COMMIT_SHA>] [<sibling-dir>]

Flips a recommendation's `applied` field from `false` to `true` in the audit
workspace's `audit/recommendations.jsonl`. The flip is atomic and concurrent-
safe (flock-guarded) so two parallel appliers working on different recs cannot
corrupt the file.

Args:
  <RECOMMENDATION_ID>   The R-NNN id to flip (must already exist in the file).
  [<COMMIT_SHA>]        Optional. Commit sha that landed the change in the
                        target repo. Stored as `applied_commit_sha`.
  [<sibling-dir>]       Audit workspace root. Defaults to $PWD. If that path
                        does not contain audit/recommendations.jsonl, the tool
                        also checks ./audit/recommendations.jsonl.

Updates per record (the matching one only):
  .applied             = true
  .applied_at          = now (ISO-8601 UTC)
  .applied_commit_sha  = <COMMIT_SHA>  (when provided; otherwise unchanged)

Exit codes:
  0  Success — record updated.
  1  Recommendation_id not found in the file.
  2  Missing arguments, or recommendations.jsonl not found.

Examples:
  tools/flip_applied.sh R-007 abc123def
  cd /path/to/__audit && tools/flip_applied.sh R-007
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 2 ;;
esac

RID="$1"
SHA="${2:-}"
SIBLING="${3:-$PWD}"

if [ -f "$SIBLING/audit/recommendations.jsonl" ]; then
  RECS="$SIBLING/audit/recommendations.jsonl"
elif [ -f "audit/recommendations.jsonl" ]; then
  RECS="audit/recommendations.jsonl"
else
  echo "recommendations.jsonl not found (looked in $SIBLING/audit/ and ./audit/)" >&2
  exit 2
fi

LOCK="${RECS}.lock"
TMP=$(mktemp "${RECS}.tmp.XXXXXX")
# Random suffix via mktemp instead of guessable PID form `${RECS}.tmp.$$`.
# Same rationale as scripts/manifest_update.sh — closes a same-UID symlink
# race window where an attacker pre-creates the predictable PID path as a
# symlink. mktemp creates with O_EXCL + 0600 in the same directory.

# Build a jq filter that updates only the matching record, leaving others
# semantically unchanged (the file is rewritten as compact JSONL). Idempotent:
# re-flipping an already-applied rec refreshes applied_at and exits 0.
# shellcheck disable=SC2016 # jq variables expand inside jq, not the shell.
FILTER='
  if .recommendation_id == $rid then
    .applied = true
    | .applied_at = $now
    | (if $sha != "" then .applied_commit_sha = $sha else . end)
  else . end
'

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# flock is required to prevent the read-modify-write race when two parallel
# appliers flip different recommendations concurrently. The previous
# warn-and-fall-through path silently corrupted recommendations.jsonl under
# load (per round-I security review). Fail hard.
if ! command -v flock >/dev/null 2>&1; then
  echo "flip_applied.sh requires flock(1); install util-linux or block concurrent invocations another way" >&2
  exit 3
fi
exec 9>"$LOCK"
flock 9
jq -c --arg rid "$RID" --arg now "$NOW" --arg sha "$SHA" "$FILTER" "$RECS" > "$TMP"
mv "$TMP" "$RECS"
flock -u 9
exec 9>&-

# Verify the rec was actually present (filter no-ops if rid missing).
if ! jq -e --arg rid "$RID" 'select(.recommendation_id == $rid and .applied == true)' "$RECS" >/dev/null 2>&1; then
  echo "no recommendation matched $RID (or applied stayed false); nothing changed" >&2
  exit 1
fi

echo "flipped $RID: applied=true, applied_at=$NOW${SHA:+, applied_commit_sha=$SHA}"
exit 0
