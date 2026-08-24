#!/bin/sh
set -eu

skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
ledger_bin=${LEDGER_BIN:-ledger}
jaq_bin=${JAQ_BIN:-jaq}
definition="$skill_root/definitions/ledger/cumulative-ablation-basis.json"
valid="$skill_root/tests/fixtures/cumulative-ablation-basis-valid.json"
tmp=$(mktemp -d "${TMPDIR:-/tmp}/actuating-ablation-basis.XXXXXX")
trap 'rm -rf "$tmp"' EXIT HUP INT TERM

expect_valid() {
  input=$1
  "$ledger_bin" materialize --definition "$definition" \
    --input "comparison=$input" --format json |
    "$jaq_bin" -e '
      .schema == "ledger-materialization-result/v1" and
      .valid == true and .storage_mutated == false and
      (.artifact_id | startswith("sha256:"))
    ' >/dev/null
}

expect_invalid() {
  name=$1
  filter=$2
  candidate="$tmp/$name.json"
  output="$tmp/$name.out.json"
  "$jaq_bin" "$filter" "$valid" >"$candidate"
  set +e
  "$ledger_bin" validate --definition "$definition" \
    --input "comparison=$candidate" --format json >"$output"
  status=$?
  set -e
  test "$status" -ne 0
  "$jaq_bin" -e '.valid == false and .storage_mutated == false' "$output" >/dev/null
}

"$ledger_bin" definition check --definition "$definition" --format json |
  "$jaq_bin" -e '.valid == true and .passive == true and .authority_granted == false' >/dev/null
expect_valid "$valid"

failed="$tmp/failed.json"
"$jaq_bin" '
  .cumulative_ablation_basis.subtractive_candidate.outcome = "failed-required-valid" |
  .cumulative_ablation_basis.subtractive_candidate.failure_refs = ["proof-valid-transition:failed"] |
  .cumulative_ablation_basis.requested_successor = "direct-repair"
' "$valid" >"$failed"
expect_valid "$failed"

expect_invalid passing-quotient-bypassed '
  .cumulative_ablation_basis.requested_successor = "direct-repair"
'
expect_invalid incomplete-factor-fold '
  .cumulative_ablation_basis.factor_dispositions =
    [.cumulative_ablation_basis.factor_dispositions[1]]
'
expect_invalid incomplete-finding-surface '
  .cumulative_ablation_basis.subtractive_candidate.tested_finding_refs = ["finding-edge"]
'
expect_invalid failed-without-evidence '
  .cumulative_ablation_basis.subtractive_candidate.outcome = "failed-required-valid" |
  .cumulative_ablation_basis.requested_successor = "direct-repair"
'
expect_invalid unresolved-factor '
  .cumulative_ablation_basis.unresolved_factor_refs = ["factor-unknown"]
'

echo "actuating cumulative ablation basis: pass"
