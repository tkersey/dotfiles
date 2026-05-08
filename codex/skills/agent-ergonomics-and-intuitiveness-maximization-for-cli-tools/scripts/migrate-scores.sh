#!/usr/bin/env bash
# scripts/migrate-scores.sh — Migrate scores from one rubric_version to another.
#
# When the rubric MAJOR version bumps, prior agent_surfaces.jsonl scores need
# to be reinterpreted under the new anchors. This script applies the
# documented transformation per migration step.
#
# Migration rules are coded as bash functions named `migrate_<from>__<to>` using
# identifier-safe versions (`1.0.0` -> `1_0_0`) so adding a new step just means
# defining a new function. The script auto-finds the migration path from --from
# to --to and chains them.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/migrate-scores.sh <input.jsonl> --from V1 --to V2 [--out PATH]

Migrate every record's scores from rubric V1 to V2 by chaining migration
steps. The output is a new JSONL file at --out (default: <input>.<V2>.jsonl).

Args:
  <input.jsonl>      Source agent_surfaces.jsonl (or any scorer output).
  --from V           Source rubric_version (semver: 1.0.0 etc.)
  --to V             Target rubric_version. Must be reachable via a chain of
                     migrate_X__Y functions defined in this script.
  --out PATH         Output path (default: <input>.<V2>.jsonl).

Behavior:
  - For each record, set rubric_version to V2; transform .scores per the
    migration chain; write to --out.
  - If V1 == V2, just copy (idempotent).
  - If a migration step is missing, exit 2 with a clear error.

Exit codes:
  0  Migration complete.
  1  Bad args / missing input.
  2  No migration path V1 → V2 (steps not defined).
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 1 ;;
esac

INPUT="$1"; shift
FROM=""; TO=""; OUT=""
need_value() {
  [ -n "${2:-}" ] || { echo "$1 requires a value" >&2; exit 1; }
  case "$2" in --*) echo "$1 requires a value, got option-like token: $2" >&2; exit 1 ;; esac
}
while [ "$#" -gt 0 ]; do
  case "$1" in
    --from) need_value "$1" "${2:-}"; FROM="$2"; shift 2 ;;
    --to)   need_value "$1" "${2:-}"; TO="$2"; shift 2 ;;
    --out)  need_value "$1" "${2:-}"; OUT="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

[ -f "$INPUT" ] || { echo "input not found: $INPUT" >&2; exit 1; }
[ -z "$FROM" ] && { echo "--from required" >&2; exit 1; }
[ -z "$TO" ]   && { echo "--to required" >&2; exit 1; }
[ -z "$OUT" ]  && OUT="${INPUT%.jsonl}.${TO}.jsonl"

input_real=$(realpath -m "$INPUT")
out_real=$(realpath -m "$OUT")
if [ "$input_real" = "$out_real" ]; then
  echo "--out must not be the same file as input; refusing to overwrite $INPUT" >&2
  exit 1
fi

# Migration step registry — add new functions as the rubric evolves.
# Each function reads stdin (one JSON record per line) and writes stdout.
# Available helpers:
#   - jq is the standard transformation tool here. Migrations are pure
#     functional rewrites of the .scores object.

# Identity migration (used when chaining to/from same version).
migrate_identity() { /bin/cat; }

# Example placeholder migrations. Real ones go here as the rubric changes.
# migrate_1_0_0__1_1_0() { jq -c '.scores.error_pedagogy = (.scores.error_pedagogy + 50)'; }
# migrate_1_1_0__2_0_0() { jq -c '.scores |= (with_entries(.value = ((.value * 0.95) | floor)))'; }

version_ident() {
  printf '%s' "$1" | sed 's/[^[:alnum:]_]/_/g'
}

# Compute migration path. For now, only support direct migrations and
# identity. A general path-finding algorithm is overkill until we have
# multiple steps.
chain_path() {
  local from="$1" to="$2"
  if [ "$from" = "$to" ]; then
    echo "migrate_identity"
    return 0
  fi
  local fn_name
  fn_name="migrate_$(version_ident "$from")__$(version_ident "$to")"
  if declare -f "$fn_name" >/dev/null 2>&1; then
    echo "$fn_name"
    return 0
  fi
  return 1
}

if ! step=$(chain_path "$FROM" "$TO"); then
  echo "no migration path defined: $FROM → $TO" >&2
  echo "  Define a function named 'migrate_$(version_ident "$FROM")__$(version_ident "$TO")' in this script and re-run." >&2
  echo "  Or run multi-hop: migrate to an intermediate version first." >&2
  exit 2
fi

n=0
: > "$OUT"
while IFS= read -r line; do
  [ -z "$line" ] && continue
  n=$((n + 1))
  # Run the chosen migration step on a single-line input; rewrite rubric_version.
  printf '%s\n' "$line" | "$step" | jq -c --arg v "$TO" '. + {rubric_version: $v}' >> "$OUT"
done < "$INPUT"

echo "migrated $n record(s) from $FROM to $TO → $OUT"
