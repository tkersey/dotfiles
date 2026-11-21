#!/usr/bin/env bash
# Exercise scripts/check-bundle against a valid fixture and one mutation per law.
set -euo pipefail

skill_root=$(cd -- "$(dirname -- "$0")/.." && pwd)
check="$skill_root/scripts/check-bundle"
fixture="$skill_root/tests/fixtures/bundle"
temp=$(mktemp -d "${TMPDIR:-/tmp}/diadoche-check.XXXXXX")
trap 'rm -rf -- "$temp"' EXIT

ledger definition check \
  --definition "$skill_root/definitions/ledger/context-bundle.json" --format json |
  jaq -e '.valid and (.authority_granted | not)' > /dev/null

jaq -n --rawfile c "$fixture/context.md" --rawfile e "$fixture/evidence.jsonl" \
  '{description: "fixture", files: {"context.md": {content: $c}, "evidence.jsonl": {content: $e}}}' \
  > "$temp/valid.json"

# Each case is written in this shell, so a broken filter stops the test.
mutate() { jaq "$2" "$temp/valid.json" > "$temp/$1.json"; }
add_evidence() { jaq --arg line "$2" '.files["evidence.jsonl"].content += $line + "\n"' \
  "$temp/valid.json" > "$temp/$1.json"; }

failures=0
expect() { # expect <valid|invalid> <bundle> [law code]
  local want=$1 bundle=$2 code=${3:-} name=${2##*/} got
  if "$check" "$bundle" > "$temp/out.json" 2> "$temp/err.txt"; then got=valid; else got=invalid; fi
  if ! jaq -e '.schema == "ledger-validation-result/v1"' "$temp/out.json" > /dev/null 2>&1; then
    echo "FAIL $name: no validation result"; cat "$temp/out.json" "$temp/err.txt"; failures=$((failures + 1)); return
  fi
  if [ "$got" != "$want" ]; then
    echo "FAIL $name: expected $want, got $got"; cat "$temp/out.json"; failures=$((failures + 1)); return
  fi
  if [ -n "$code" ] && ! jaq -e --arg c "$code" '[.errors[].code] | index($c) != null' "$temp/out.json" > /dev/null; then
    echo "FAIL $name: expected law $code"; cat "$temp/out.json"; failures=$((failures + 1)); return
  fi
  echo "ok   $want $name"
}

mutate gist '. + {schema: "ledger-gist/v1", revision: "0000000000000000000000000000000000000000"}'
mutate context-only '.files |= del(.["evidence.jsonl"]) | .files["context.md"].content |= sub("  - evidence.jsonl\n"; "")'
mutate extra-file '.files["notes.txt"] = {content: "not part of the bundle"}'
mutate missing-evidence '.files |= del(.["evidence.jsonl"])'
mutate missing-context '.files |= del(.["context.md"])'
mutate no-front-matter '.files["context.md"].content |= ltrimstr("---\n")'
mutate format-v2 '.files["context.md"].content |= sub("diadoche-context/v1"; "diadoche-context/v2")'
mutate unknown-file-name '.files["context.md"].content |= sub("  - evidence.jsonl\n"; "  - evidence.jsonl\n  - patch.diff\n")'
mutate duplicate-source '.files["context.md"].content |= sub("sources:\n"; "sources:\n  - id: s1\n    description: duplicate\n")'
add_evidence duplicate-evidence '{"id":"e2","source":"s1","kind":"message","text":"x","excerpt":false}'
add_evidence undeclared-source '{"id":"e3","source":"s9","kind":"message","text":"x","excerpt":false}'
add_evidence unknown-kind '{"id":"e3","source":"s1","kind":"note","text":"x","excerpt":false}'
add_evidence string-excerpt '{"id":"e3","source":"s1","kind":"message","text":"x","excerpt":"no"}'
add_evidence missing-id '{"source":"s1","kind":"message","text":"x","excerpt":false}'
add_evidence string-source-line '{"id":"e3","source":"s1","kind":"message","text":"x","excerpt":false,"source_line":"12"}'
add_evidence unparsable-line '{not json'

expect valid "$temp/valid.json"
expect valid "$fixture"
ln -s "$skill_root" "$temp/linked-skill"
check="$temp/linked-skill/scripts/check-bundle"
expect valid "$fixture" # through a symlinked install
check="$skill_root/scripts/check-bundle"
expect valid "$temp/gist.json"
expect valid "$temp/context-only.json"
expect valid "$temp/extra-file.json"
expect invalid "$temp/missing-evidence.json" reference-exists
expect invalid "$temp/missing-context.json" exact-object
expect invalid "$temp/no-front-matter.json" exact-object
expect invalid "$temp/format-v2.json" enum
expect invalid "$temp/unknown-file-name.json" all
expect invalid "$temp/duplicate-source.json" keyed-unique
expect invalid "$temp/duplicate-evidence.json" keyed-unique
expect invalid "$temp/undeclared-source.json" reference-exists
expect invalid "$temp/unknown-kind.json" all
expect invalid "$temp/string-excerpt.json" all
expect invalid "$temp/missing-id.json" keyed-unique
expect invalid "$temp/string-source-line.json" all
expect invalid "$temp/unparsable-line.json" bounded-array

if [ "$failures" -ne 0 ]; then echo "$failures failure(s)"; exit 1; fi
echo "all check-bundle cases passed"
