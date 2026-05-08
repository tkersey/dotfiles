#!/usr/bin/env bash
# scripts/dirty-surfaces.sh — Compute which surfaces need re-scoring.
#
# Phase 6 (re-score) wastefully re-runs every scorer against every surface
# even when only a handful of source files changed. This script intersects
# git's "what changed since X" with the inventory's evidence.path to return
# ONLY the surfaces whose evidence actually moved.
#
# Use: pipe the output to a re-score loop. For 200 surfaces and a Phase-5
# commit touching 4 files, this typically returns 5-15 surfaces — a 10-40x
# reduction in re-score cost.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/dirty-surfaces.sh <sibling> <target> [--since REF] [--format json|ids]

Identify surfaces whose evidence files changed in the target since REF.

Args:
  <sibling>         Audit workspace root (with audit/surface_inventory.jsonl).
  <target>          Target repo absolute path.
  --since REF       Git ref (default: HEAD~1). Anything git rev-parse accepts.
  --format FORMAT   ids   - one surface_id per line (default).
                    json  - JSONL with surface_id + evidence_path + change_kind.

Behavior:
  1. Read each surface's evidence.path from surface_inventory.jsonl.
  2. Run `git diff --name-only <REF> HEAD` in target.
  3. For each surface with evidence.path matching a changed file, output it.
  4. Surfaces lacking evidence.path are conservatively included only when
     --include-no-evidence is passed (default: skip them, they're stale).

Output to stdout:
  ids: one surface_id per line.
  json: jsonl with {surface_id, evidence_path, change_kind} per record.

Exit codes:
  0  Output produced (zero or more lines).
  1  Bad args / missing inputs.
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

die() {
  echo "$*" >&2
  exit 1
}
need_value() {
  [ -n "${2:-}" ] || die "$1 requires a value"
  case "$2" in --*) die "$1 requires a value, got option-like token: $2" ;; esac
}

[ -z "${2:-}" ] && { usage >&2; exit 1; }
SIBLING="$1"
TARGET="$2"
shift 2

SINCE="HEAD~1"
FORMAT=ids
INCLUDE_NO_EVIDENCE=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --since)
      need_value "$1" "${2:-}"
      SINCE="$2"; shift 2
      ;;
    --format)
      need_value "$1" "${2:-}"
      FORMAT="$2"; shift 2
      ;;
    --include-no-evidence)    INCLUDE_NO_EVIDENCE=1; shift ;;
    *) die "unknown arg: $1" ;;
  esac
done

case "$FORMAT" in ids|json) ;; *) die "bad --format: $FORMAT" ;; esac

INV="$SIBLING/audit/surface_inventory.jsonl"
[ -f "$INV" ] || die "no inventory: $INV"
git -C "$TARGET" rev-parse --git-dir >/dev/null 2>&1 || die "target is not a git repo: $TARGET"

# Get changed files since REF.
if ! git -C "$TARGET" rev-parse "$SINCE" >/dev/null 2>&1; then
  echo "git ref not found in target: $SINCE" >&2
  exit 1
fi
# For each changed file, find surfaces whose evidence.path equals or has it
# as a suffix (handles paths like "src/cli.rs" vs "/abs/path/src/cli.rs").
# Use a python helper for the matching — bash + jq is too slow for 200+
# surfaces × N changed files.
#
# Let Python call `git diff -z` directly so filenames with spaces, quotes,
# backslashes, non-ASCII, or newlines remain exact NUL-delimited paths.
python3 - "$INV" "$INCLUDE_NO_EVIDENCE" "$FORMAT" "$TARGET" "$SINCE" <<'PY'
import json, subprocess, sys

inv_path = sys.argv[1]
include_no_evidence = sys.argv[2] == "1"
fmt = sys.argv[3]
target = sys.argv[4]
since = sys.argv[5]

raw_changed = subprocess.check_output(
    ["git", "-C", target, "diff", "-z", "--name-only", since, "HEAD"]
)
changed_set = {
    part.decode("utf-8", "surrogateescape")
    for part in raw_changed.split(b"\0")
    if part
}
if not changed_set:
    sys.exit(0)

with open(inv_path) as f:
    surfaces = [json.loads(line) for line in f if line.strip()]

dirty = []
for s in surfaces:
    sid = s.get('surface_id', '')
    ev = s.get('evidence', {})
    ev_path = ev.get('path', '') if isinstance(ev, dict) else ''
    if not ev_path:
        if include_no_evidence:
            dirty.append({'surface_id': sid, 'evidence_path': '', 'change_kind': 'no-evidence-conservative'})
        continue
    # Match: exact OR ev_path is a suffix of any changed file OR vice-versa.
    matched = None
    for cf in changed_set:
        if ev_path == cf or ev_path.endswith('/' + cf) or cf.endswith('/' + ev_path) or cf == ev_path:
            matched = cf
            break
    if matched:
        dirty.append({'surface_id': sid, 'evidence_path': ev_path, 'change_kind': 'modified'})

if fmt == 'json':
    for d in dirty:
        print(json.dumps(d))
else:
    for d in dirty:
        print(d['surface_id'])
PY
