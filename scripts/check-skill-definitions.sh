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
materialization_count=0
contract_count=0
transaction_count=0

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
              fixture_name=${fixture##*/}
              expectation="$fixture_root/expected/${fixture_name%.json}.materialization.json"
              if [[ -f "$expectation" ]]; then
                materialization_count=$((materialization_count + 1))
                expected_content=$(jq -S -c '.canonical_content' "$expectation")
                "$ledger_bin" materialize \
                  --definition "$definition" \
                  --input "$input_name=$fixture" \
                  --format json |
                  jq -e \
                    --arg expected_content "$expected_content" \
                    --slurpfile expectation "$expectation" \
                    '.valid == true and
                     .artifact_id == $expectation[0].artifact_id and
                     .canonical_content_digest ==
                       $expectation[0].canonical_content_digest and
                     .canonical_content == $expected_content and
                     .authority_granted == false and
                     .storage_mutated == false' >/dev/null
              fi
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

plan_policy_definition=codex/skills/plan/definitions/ledger/plan-policy-document.json
plan_policy_fixture=codex/skills/plan/definitions/fixtures/ledger/execution-policy-graph/valid/complete.json
plan_id=$(jq -r '.execution_policy_graph.plan_id' "$plan_policy_fixture")
plan_tmp=$(mktemp -d)
plan_repo=$(cd "$plan_tmp" && pwd -P)
create_result=$(
  "$ledger_bin" transact \
    --definition "$plan_policy_definition" \
    --operation create \
    --repo "$plan_repo" \
    --input "policy=$plan_policy_fixture" \
    --param "plan_id=$plan_id" \
    --format json
)
transaction_count=$((transaction_count + 1))
jq -e \
  --arg plan_id "$plan_id" \
  '.schema == "ledger-transaction-result/v1" and
   .definition.id == "plan/plan-policy-document" and
   .definition.abi == "ledger-artifact-abi/v1" and
   .operation == "create" and
   .effects[0].logical_ref == ("plan/" + $plan_id + "/policy.json") and
   (.returned_content | fromjson |
     .execution_policy_graph.plan_id == $plan_id) and
   .semantic_authority_granted == false and
   .storage_mutated == true' \
  <<<"$create_result" >/dev/null
created_revision=$(jq -r '.effects[0].revision_after' <<<"$create_result")

project_result=$(
  "$ledger_bin" project \
    --definition "$plan_policy_definition" \
    --projection show \
    --repo "$plan_repo" \
    --param "plan_id=$plan_id" \
    --format json
)
jq -e \
  --arg plan_id "$plan_id" \
  --arg revision "$created_revision" \
  '.schema == "ledger-projection-result/v1" and
   .definition.id == "plan/plan-policy-document" and
   .projection == "show" and
   .store.logical_ref == ("plan/" + $plan_id + "/policy.json") and
   .store.revision == $revision and
   .data.execution_policy_graph.plan_id == $plan_id and
   .authority_granted == false and
   .storage_mutated == false' \
  <<<"$project_result" >/dev/null

set +e
missing_revision_result=$(
  "$ledger_bin" transact \
    --definition "$plan_policy_definition" \
    --operation revise \
    --repo "$plan_repo" \
    --input "policy=$plan_policy_fixture" \
    --param "plan_id=$plan_id" \
    --param request_id=revision-smoke \
    --format json
)
missing_revision_status=$?
set -e
[[ "$missing_revision_status" -eq 2 ]]
jq -e \
  '.schema == "ledger-transaction-error/v1" and
   .code == "MissingOperationParameter" and
   .semantic_authority_granted == false' \
  <<<"$missing_revision_result" >/dev/null

revise_result=$(
  "$ledger_bin" transact \
    --definition "$plan_policy_definition" \
    --operation revise \
    --repo "$plan_repo" \
    --input "policy=$plan_policy_fixture" \
    --param "plan_id=$plan_id" \
    --param request_id=revision-smoke \
    --param "expected_revision=$created_revision" \
    --format json
)
transaction_count=$((transaction_count + 1))
jq -e \
  --arg plan_id "$plan_id" \
  '.schema == "ledger-transaction-result/v1" and
   .definition.id == "plan/plan-policy-document" and
   .operation == "revise" and
   .effects[0].logical_ref == ("plan/" + $plan_id + "/policy.json") and
   .effects[0].result == "replaced" and
   .semantic_authority_granted == false and
   .storage_mutated == true' \
  <<<"$revise_result" >/dev/null
rm -rf -- "$plan_tmp"

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
  'definition conformance passed: manifests=%d seq=%d ledger=%d fixtures=%d materializations=%d transactions=%d contracts=%d\n' \
  "$manifest_count" \
  "$seq_count" \
  "$ledger_count" \
  "$fixture_count" \
  "$materialization_count" \
  "$transaction_count" \
  "$contract_count"
