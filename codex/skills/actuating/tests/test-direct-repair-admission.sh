#!/bin/sh
set -eu

skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
ledger_bin=${LEDGER_BIN:-ledger}
jaq_bin=${JAQ_BIN:-jaq}
definition="$skill_root/definitions/ledger/direct-repair-admission.json"
valid="$skill_root/tests/fixtures/direct-repair-admission-valid.json"
tmp=$(mktemp -d "${TMPDIR:-/tmp}/actuating-direct-repair-gate.XXXXXX")
trap 'rm -rf "$tmp"' EXIT HUP INT TERM

expect_valid() {
  input=$1
  output=$2
  "$ledger_bin" materialize \
    --definition "$definition" \
    --input "gate=$input" \
    --format json >"$output"
  "$jaq_bin" -e '
    .schema == "ledger-materialization-result/v1" and
    .valid == true and
    .storage_mutated == false and
    (.artifact_id | startswith("sha256:"))
  ' "$output" >/dev/null
}

expect_invalid() {
  name=$1
  filter=$2
  candidate="$tmp/$name.json"
  output="$tmp/$name.out.json"
  "$jaq_bin" "$filter" "$valid" >"$candidate"
  set +e
  "$ledger_bin" validate \
    --definition "$definition" \
    --input "gate=$candidate" \
    --format json >"$output"
  status=$?
  set -e
  if [ "$status" -eq 0 ]; then
    echo "expected direct-repair admission rejection: $name" >&2
    exit 1
  fi
  "$jaq_bin" -e '
    .schema == "ledger-validation-result/v1" and
    .valid == false and
    .storage_mutated == false
  ' "$output" >/dev/null
}

expect_invalid_input() {
  name=$1
  candidate=$2
  output="$tmp/$name.out.json"
  set +e
  "$ledger_bin" validate \
    --definition "$definition" \
    --input "gate=$candidate" \
    --format json >"$output"
  status=$?
  set -e
  if [ "$status" -eq 0 ]; then
    echo "expected direct-repair admission rejection: $name" >&2
    exit 1
  fi
  "$jaq_bin" -e '
    .schema == "ledger-validation-result/v1" and
    .valid == false and
    .storage_mutated == false
  ' "$output" >/dev/null
}

"$ledger_bin" definition check \
  --definition "$definition" \
  --format json |
  "$jaq_bin" -e '
    .schema == "ledger-definition-check-result/v1" and
    .valid == true and
    .passive == true and
    .authority_granted == false
  ' >/dev/null

expect_valid "$valid" "$tmp/ordinary.out.json"

retain="$tmp/retain-theory-reprove.json"
"$jaq_bin" '
  .direct_repair_admission.mutation_basis = "retain-theory-reprove" |
  .direct_repair_admission.active_elimination_lease = "revoked" |
  .direct_repair_admission.failed_premise = "realization" |
  .direct_repair_admission.premise_evidence = {
    "kind": "realization",
    "evidence_refs": ["diff:restored-realization"]
  }
' "$valid" >"$retain"
expect_valid "$retain" "$tmp/retain.out.json"

generated_output="$tmp/retain-generated-output.json"
"$jaq_bin" '
  .direct_repair_admission.mutation_basis = "retain-theory-reprove" |
  .direct_repair_admission.active_elimination_lease = "revoked" |
  .direct_repair_admission.failed_premise = "generated-output" |
  .direct_repair_admission.premise_evidence = {
    "kind": "generated-output",
    "generator_ref": "generator-invalid-transition",
    "predecessor_source_digest": "sha256:1212121212121212121212121212121212121212121212121212121212121212",
    "successor_source_digest": "sha256:1212121212121212121212121212121212121212121212121212121212121212",
    "generated_output_digest": "sha256:3434343434343434343434343434343434343434343434343434343434343434",
    "evidence_refs": ["generator:transition-output"]
  }
' "$valid" >"$generated_output"
expect_valid "$generated_output" "$tmp/retain-generated-output.out.json"

artifact_binding="$tmp/retain-artifact-binding.json"
"$jaq_bin" '
  .direct_repair_admission.mutation_basis = "retain-theory-reprove" |
  .direct_repair_admission.active_elimination_lease = "revoked" |
  .direct_repair_admission.failed_premise = "artifact-binding" |
  .direct_repair_admission.premise_evidence = {
    "kind": "artifact-binding",
    "artifact_ref": "release/example.tar.zst",
    "expected_artifact_digest": "sha256:5656565656565656565656565656565656565656565656565656565656565656",
    "actual_artifact_digest": "sha256:5656565656565656565656565656565656565656565656565656565656565656",
    "evidence_refs": ["artifact:binding-readback"]
  }
' "$valid" >"$artifact_binding"
expect_valid "$artifact_binding" "$tmp/retain-artifact-binding.out.json"

expect_invalid semantic-model-change '
  .direct_repair_admission.theory.successor_semantic_model_digest =
    "sha256:1111111111111111111111111111111111111111111111111111111111111111"
'

expect_invalid semantic-constructor-added '
  .direct_repair_admission.semantic_constructor_delta =
    ["transition:retrying"]
'

expect_invalid member-specific-factor-added '
  .direct_repair_admission.member_specific_factor_refs =
    ["factor-invalid-reset-special-case"]
'

expect_invalid enforcement-site-added '
  .direct_repair_admission.new_enforcement_site_refs =
    ["owner-downstream-validator"]
'

expect_invalid factor-disposition-omitted '
  .direct_repair_admission.factor_dispositions = []
'

expect_invalid unknown-generator '
  .direct_repair_admission.class_mappings[0].generator_ref =
    "generator-unknown"
'

expect_invalid multiple-generators '
  .direct_repair_admission.theory.causal_generators += [
    (.direct_repair_admission.theory.causal_generators[0] |
      .generator_id = "generator-second")
  ]
'

expect_invalid revoked-without-localization '
  .direct_repair_admission.active_elimination_lease = "revoked"
'

expect_invalid premise-evidence-kind-mismatch '
  .direct_repair_admission.mutation_basis = "retain-theory-reprove" |
  .direct_repair_admission.active_elimination_lease = "revoked" |
  .direct_repair_admission.failed_premise = "proof" |
  .direct_repair_admission.premise_evidence = {
    "kind": "realization",
    "evidence_refs": ["proof:mismatch"]
  }
'

expect_invalid generated-output-without-artifact-evidence '
  .direct_repair_admission.mutation_basis = "retain-theory-reprove" |
  .direct_repair_admission.active_elimination_lease = "revoked" |
  .direct_repair_admission.failed_premise = "generated-output" |
  .direct_repair_admission.premise_evidence = {"kind": "generated-output"}
'

generated_source_changed="$tmp/generated-output-source-changed.json"
"$jaq_bin" '
  .direct_repair_admission.premise_evidence.successor_source_digest =
    "sha256:7878787878787878787878787878787878787878787878787878787878787878"
' "$generated_output" >"$generated_source_changed"
expect_invalid_input generated-output-source-changed "$generated_source_changed"

generated_unknown="$tmp/generated-output-unknown-generator.json"
"$jaq_bin" '
  .direct_repair_admission.premise_evidence.generator_ref =
    "generator-unknown"
' "$generated_output" >"$generated_unknown"
expect_invalid_input generated-output-unknown-generator "$generated_unknown"

artifact_missing="$tmp/artifact-binding-missing-actual.json"
"$jaq_bin" '
  del(.direct_repair_admission.premise_evidence.actual_artifact_digest)
' "$artifact_binding" >"$artifact_missing"
expect_invalid_input artifact-binding-missing-actual "$artifact_missing"

artifact_mismatch="$tmp/artifact-binding-mismatch.json"
"$jaq_bin" '
  .direct_repair_admission.premise_evidence.actual_artifact_digest =
    "sha256:9090909090909090909090909090909090909090909090909090909090909090"
' "$artifact_binding" >"$artifact_mismatch"
expect_invalid_input artifact-binding-mismatch "$artifact_mismatch"

expect_invalid semantic-premise-is-not-restoration '
  .direct_repair_admission.mutation_basis = "retain-theory-reprove" |
  .direct_repair_admission.active_elimination_lease = "revoked" |
  .direct_repair_admission.failed_premise = "source-topology"
'

expect_invalid restoration-generator-unknown '
  .direct_repair_admission.restoration.generator_refs =
    ["generator-unknown"]
'

echo "actuating direct-repair admission gate: pass"
