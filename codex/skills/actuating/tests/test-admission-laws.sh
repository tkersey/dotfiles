#!/bin/sh
set -eu

skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
ledger_bin=${LEDGER_BIN:-ledger}
jaq_bin=${JAQ_BIN:-jaq}
construction_definition="$skill_root/definitions/ledger/construction-contract.json"
evidence_definition="$skill_root/definitions/ledger/evidence-protocol.json"
receipt_definition="$skill_root/definitions/ledger/construction-registration-receipt.json"
valid_construction="$skill_root/tests/fixtures/construction-valid.json"
valid_receipt="$skill_root/tests/fixtures/registration-receipt-valid.json"
test_root=$(mktemp -d "${TMPDIR:-/tmp}/actuating-admission-laws.XXXXXX")
trap 'rm -rf "$test_root"' EXIT HUP INT TERM

expect_valid() {
  definition=$1
  input_name=$2
  input_file=$3
  "$ledger_bin" validate \
    --definition "$definition" \
    --input "$input_name=$input_file" \
    | "$jaq_bin" -e '.valid == true' >/dev/null
}

expect_invalid() {
  definition=$1
  input_name=$2
  input_file=$3
  if "$ledger_bin" validate \
    --definition "$definition" \
    --input "$input_name=$input_file" \
    | "$jaq_bin" -e '.valid == true' >/dev/null 2>&1; then
    echo "expected rejection: $input_file" >&2
    exit 1
  fi
}

mutate_and_reject() {
  name=$1
  filter=$2
  output="$test_root/$name.json"
  "$jaq_bin" "$filter" "$valid_construction" > "$output"
  expect_invalid "$construction_definition" construction "$output"
}

expect_valid "$construction_definition" construction "$valid_construction"
expect_valid "$receipt_definition" receipt "$valid_receipt"

mutate_and_reject duplicate-element-claim \
  '.artifact.payload.carrier_claims += [(.artifact.payload.carrier_claims[0] | .claim_id = "claim.second")] | .artifact.payload.carrier_claim_refs += ["claim.second"]'
mutate_and_reject invented-predecessor-factor \
  '.artifact.payload.carrier_claims[0] |= (.disposition = "closed-existing" | .predecessor_construction_ref = "sha256:3333333333333333333333333333333333333333333333333333333333333333" | .predecessor_factor_refs = ["factor.invented"] | .presence_obligation_ref = "obligation.impl" | .closure_obligation_ref = "obligation.impl" | .negative_obligation_ref = null | .presence_receipt_ref = "sha256:4444444444444444444444444444444444444444444444444444444444444444" | .closure_receipt_ref = "sha256:5555555555555555555555555555555555555555555555555555555555555555" | .structural_resolution_refs = [])'
mutate_and_reject invented-structural-resolution \
  '.artifact.payload.carrier_claims[0].structural_resolution_refs = ["factor.invented"]'
mutate_and_reject obstructed-normal-form \
  '.artifact.payload.recompilation.adjudication.reduction_disposition = "obstructed"'
mutate_and_reject mismatched-verifier-digest \
  '.artifact.payload.proof_obligations[0].verifier.argv = ["false"]'

bad_receipt="$test_root/bad-receipt.json"
"$jaq_bin" '.receipt.step_id = "obligation.other"' "$valid_receipt" > "$bad_receipt"
expect_invalid "$receipt_definition" receipt "$bad_receipt"

for definition_file in "$skill_root"/definitions/ledger/*.json; do
  "$ledger_bin" definition check --definition "$definition_file" \
    | "$jaq_bin" -e '.valid == true' >/dev/null
done

"$jaq_bin" -e '
  .constraints.terms.t26[1][0][0] == "subject#" and
  (.constraints.state.admissions[2].actions | any(. == ["clear", "subject"]) | not) and
  (.constraints.state.admissions[18].requires | index("subject")) != null and
  (.constraints.state.admissions[18].laws | any(. == ["use", "t28"])) and
  (.constraints.state.admissions[18].laws | any(. == ["use", "t42"])) and
  (.constraints.state.admissions[18].laws | any(. == ["bounded-array", "event#/body/construction/artifact/payload/counterexample_theory/set_refs", null, 0])) and
  (.constraints.state.admissions[19].laws | any(. == ["use", "t42"]))
' "$evidence_definition" >/dev/null

echo "actuating admission laws: pass"
