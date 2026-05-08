#!/usr/bin/env bash
# scripts/validate-artifacts-strict.sh — Formal JSON Schema validation.
#
# Validates every artifact in <sibling>/audit/ against its corresponding
# schema in assets/schemas/. Unlike the lighter `validate_pass.sh` (existence
# + jq-must-parse), this enforces FULL schema conformance:
#   - all required fields present
#   - field types match
#   - enums respected
#   - no additional properties beyond schema (when additionalProperties=false)
#
# Use this as the last gate before declaring a pass complete. Use the lighter
# validator for in-flight checks during phases.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/validate-artifacts-strict.sh <sibling> [--skill-path PATH]

Validate all audit artifacts against assets/schemas/*.schema.json.

Args:
  <sibling>       Audit workspace root.
  --skill-path P  Override skill location (default: parent of this script).

Validated:
  audit/manifest.json              vs manifest.schema.json
  audit/surface_inventory.jsonl    vs surface_inventory.schema.json (per-line)
  audit/agent_surfaces.jsonl       vs agent_surfaces.schema.json (per-line)
  audit/recommendations.jsonl      vs recommendations.schema.json (per-line)
  audit/applied_changes.jsonl      vs applied_changes.schema.json (per-line)
  audit/intent_inference_corpus.jsonl  vs intent_inference_corpus.schema.json (per-line)
  audit/telemetry.jsonl            vs telemetry.schema.json (per-line)

Output:
  Per-file status block; final FAIL list if any record failed.

Exit codes:
  0  All artifacts conform.
  1  At least one validation failure.
  2  Bad args / missing tools (jsonschema lib missing).
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "")        usage >&2; exit 2 ;;
esac

SIBLING="$1"; shift
SKILL_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
need_value() {
  [ -n "${2:-}" ] || { echo "$1 requires a value" >&2; exit 2; }
  case "$2" in --*) echo "$1 requires a value, got option-like token: $2" >&2; exit 2 ;; esac
}
while [ "$#" -gt 0 ]; do
  case "$1" in
    --skill-path) need_value "$1" "${2:-}"; SKILL_PATH="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

SCHEMAS="$SKILL_PATH/assets/schemas"
[ -d "$SCHEMAS" ] || { echo "schemas dir not found: $SCHEMAS" >&2; exit 2; }
[ -d "$SIBLING/audit" ] || { echo "audit dir not found: $SIBLING/audit" >&2; exit 2; }

if ! python3 -c 'import jsonschema' 2>/dev/null; then
  echo "python3 jsonschema library missing. Install with: pip install jsonschema" >&2
  exit 2
fi

# (artifact_path, schema_filename, mode=jsonl|json) tuples.
total_failures=0
total_files=0

validate_one() {
  local path="$1" schema_file="$2" mode="$3"
  local schema="$SCHEMAS/$schema_file"
  total_files=$((total_files + 1))

  if [ ! -f "$path" ]; then
    echo "[skip]  $path (not present)"
    return 0
  fi
  if [ ! -f "$schema" ]; then
    echo "[skip]  $path (schema $schema_file not found)"
    return 0
  fi

  local fail_count=0
  if [ "$mode" = jsonl ]; then
    fail_count=$(python3 - "$path" "$schema" <<'PY'
import json, sys
import jsonschema
path, schema_path = sys.argv[1], sys.argv[2]
with open(schema_path) as f: schema = json.load(f)
v = jsonschema.Draft202012Validator(schema)
fails = 0
with open(path) as f:
    for n, line in enumerate(f, 1):
        line = line.strip()
        if not line: continue
        try:
            rec = json.loads(line)
        except Exception as e:
            print(f"  line {n}: bad JSON: {e}", file=sys.stderr)
            fails += 1; continue
        errs = sorted(v.iter_errors(rec), key=lambda e: e.path)
        if errs:
            fails += 1
            for e in errs[:3]:
                ep = ".".join(str(p) for p in e.absolute_path) or "<root>"
                print(f"  line {n}: {ep}: {e.message}", file=sys.stderr)
print(fails)
PY
)
  else
    fail_count=$(python3 - "$path" "$schema" <<'PY'
import json, sys
import jsonschema
path, schema_path = sys.argv[1], sys.argv[2]
with open(schema_path) as f: schema = json.load(f)
with open(path) as f: doc = json.load(f)
v = jsonschema.Draft202012Validator(schema)
errs = sorted(v.iter_errors(doc), key=lambda e: e.path)
for e in errs[:5]:
    ep = ".".join(str(p) for p in e.absolute_path) or "<root>"
    print(f"  {ep}: {e.message}", file=sys.stderr)
print(1 if errs else 0)
PY
)
  fi

  if [ "$fail_count" -eq 0 ]; then
    echo "[pass]  $path"
  else
    echo "[FAIL]  $path  ($fail_count record(s) invalid)"
    total_failures=$((total_failures + fail_count))
  fi
}

echo "## Strict artifact validation"
echo
validate_one "$SIBLING/audit/manifest.json"             manifest.schema.json                   json
validate_one "$SIBLING/audit/surface_inventory.jsonl"   surface_inventory.schema.json          jsonl
validate_one "$SIBLING/audit/agent_surfaces.jsonl"      agent_surfaces.schema.json             jsonl
validate_one "$SIBLING/audit/recommendations.jsonl"     recommendations.schema.json            jsonl
validate_one "$SIBLING/audit/applied_changes.jsonl"     applied_changes.schema.json            jsonl
validate_one "$SIBLING/audit/intent_inference_corpus.jsonl"  intent_inference_corpus.schema.json    jsonl
validate_one "$SIBLING/audit/telemetry.jsonl"           telemetry.schema.json                  jsonl

echo
echo "## Summary"
echo "- files inspected: $total_files"
echo "- failed records: $total_failures"

if [ "$total_failures" -gt 0 ]; then
  echo
  echo "VALIDATION FAILED."
  exit 1
fi
echo "VALIDATION PASSED."
exit 0
