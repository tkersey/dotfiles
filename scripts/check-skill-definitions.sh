#!/usr/bin/env bash
set -euo pipefail

repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"

seq_bin=${SEQ_BIN:-seq}
ledger_bin=${LEDGER_BIN:-ledger}

command -v jq >/dev/null
command -v "$seq_bin" >/dev/null
command -v "$ledger_bin" >/dev/null

manifests=$(rg --files codex/skills | LC_ALL=C sort | grep '/definitions/manifest\.json$' || true)
if [[ -z "$manifests" ]]; then
  echo "no skill definition manifests found" >&2
  exit 1
fi

manifest_count=0
seq_count=0
ledger_count=0
fixture_count=0
contract_count=0

for manifest in $manifests; do
  manifest_count=$((manifest_count + 1))
  definition_root=${manifest%/manifest.json}
  skill_root=${definition_root%/definitions}
  expected_skill=${skill_root##*/}

  jq -e \
    --arg skill "$expected_skill" \
    '
      type == "object" and
      (keys | sort) == ["ledger", "schema", "seq", "skill"] and
      .schema == "skill-definition-set/v1" and
      .skill == $skill and
      (.seq | type == "array") and
      (.ledger | type == "array") and
      all(.seq[], .ledger[];
        type == "object" and
        (keys | sort) == ["id", "path"] and
        (.id | type == "string" and length > 0) and
        (.path | type == "string" and length > 0) and
        (.path | startswith("/") | not) and
        (.path | split("/") | all(. != "" and . != "." and . != ".."))
      )
    ' \
    "$manifest" >/dev/null

  while IFS=$'\t' read -r id path; do
    [[ -n "$id" && -n "$path" ]]
    definition="$definition_root/$path"
    [[ -f "$definition" && ! -L "$definition" ]]
    case "$path" in
      seq/*)
        seq_count=$((seq_count + 1))
        "$seq_bin" definition check \
          --definition "$definition" \
          --format json |
          jq -e '.valid == true and .authority_granted == false' >/dev/null
        ;;
      ledger/*)
        ledger_count=$((ledger_count + 1))
        "$ledger_bin" definition check \
          --definition "$definition" \
          --format json |
          jq -e '.valid == true and .authority_granted == false' >/dev/null

        input_count=$(jq '.inputs | length' "$definition")
        fixture_root="$definition_root/fixtures/ledger/${id##*/}"
        if [[ -d "$fixture_root" ]]; then
          if [[ "$input_count" -ne 1 ]]; then
            echo "$fixture_root requires an explicit multi-input fixture runner" >&2
            exit 1
          fi
          input_name=$(jq -r '.inputs | keys[0]' "$definition")
          if [[ -d "$fixture_root/valid" ]]; then
            while IFS= read -r fixture; do
              fixture_count=$((fixture_count + 1))
              "$ledger_bin" validate \
                --definition "$definition" \
                --input "$input_name=$fixture" \
                --format json |
                jq -e \
                  '.valid == true and
                   .authority_granted == false and
                   .storage_mutated == false' >/dev/null
            done < <(find "$fixture_root/valid" -type f | LC_ALL=C sort)
          fi
          if [[ -d "$fixture_root/invalid" ]]; then
            while IFS= read -r fixture; do
              fixture_count=$((fixture_count + 1))
              set +e
              result=$(
                "$ledger_bin" validate \
                  --definition "$definition" \
                  --input "$input_name=$fixture" \
                  --format json
              )
              status=$?
              set -e
              [[ "$status" -eq 2 ]]
              jq -e \
                '.valid == false and
                 .authority_granted == false and
                 .storage_mutated == false' \
                <<<"$result" >/dev/null
            done < <(find "$fixture_root/invalid" -type f | LC_ALL=C sort)
          fi
        fi
        ;;
      *)
        echo "$manifest references a definition outside seq/ or ledger/: $path" >&2
        exit 1
        ;;
    esac
  done < <(jq -r '.seq[], .ledger[] | [.id, .path] | @tsv' "$manifest")
done

tune_definition=codex/skills/tune/definitions/ledger/skill-decision-contract.json
while IFS= read -r contract; do
  contract_count=$((contract_count + 1))
  "$ledger_bin" validate \
    --definition "$tune_definition" \
    --input "contract=$contract" \
    --format json |
    jq -e \
      '.valid == true and
       .authority_granted == false and
       .storage_mutated == false' >/dev/null
done < <(
  rg --files codex/skills |
    grep '/references/decision-contract\.json$' |
    LC_ALL=C sort
)

if rg --files codex | grep -q '/decision-contract\.ya\?ml$'; then
  echo "machine-consumed decision-contract YAML remains" >&2
  exit 1
fi

printf \
  'definition conformance passed: manifests=%d seq=%d ledger=%d fixtures=%d contracts=%d\n' \
  "$manifest_count" \
  "$seq_count" \
  "$ledger_count" \
  "$fixture_count" \
  "$contract_count"
