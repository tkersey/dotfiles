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
  .direct_repair_admission.failed_premise = "realization"
' "$valid" >"$retain"
expect_valid "$retain" "$tmp/retain.out.json"

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

expect_invalid revoked-without-localization '
  .direct_repair_admission.active_elimination_lease = "revoked"
'

expect_invalid restoration-generator-unknown '
  .direct_repair_admission.restoration.generator_refs =
    ["generator-unknown"]
'

echo "actuating direct-repair admission gate: pass"
