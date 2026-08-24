#!/bin/sh
set -eu

skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
jaq_bin=${JAQ_BIN:-jaq}
fixture="$skill_root/tests/fixtures/cumulative-ablation-scenarios.json"

"$jaq_bin" -e '
  def allowed_disposition($value):
    (["preserve", "replace", "collapse", "retire", "privatize",
      "distinct-obligation"] | index($value)) != null;

  def evaluate:
    .input as $i |
    if $i.retained_corpus_complete != true then
      {valid:false, error:"retained-corpus-incomplete", selected:$i.selected}
    elif $i.causal_basis_complete != true then
      {valid:false, error:"causal-basis-incomplete", selected:$i.selected}
    elif $i.factor_fold_complete != true or
         ($i.factor_dispositions | length) == 0 then
      {valid:false, error:"factor-fold-incomplete", selected:$i.selected}
    elif any($i.factor_dispositions[]; (allowed_disposition(.) | not)) then
      {valid:false, error:"unknown-factor-disposition", selected:$i.selected}
    elif $i.subtractive.attempted != true then
      {valid:false, error:"subtractive-candidate-not-executed", selected:$i.selected}
    elif $i.subtractive.same_finding_surface != true or
         $i.subtractive.required_valid_surface != true or
         $i.subtractive.compatibility_surface != true then
      {valid:false, error:"subtractive-proof-surface-mismatch", selected:$i.selected}
    elif $i.subtractive.outcome == "passed" and
         $i.selected != "subtractive" then
      {valid:false, error:"passing-subtractive-candidate-bypassed", selected:$i.selected}
    elif $i.subtractive.outcome == "passed" and
         ($i.subtractive.failure_refs | length) != 0 then
      {valid:false, error:"passing-subtractive-has-failure", selected:$i.selected}
    elif $i.subtractive.outcome != "passed" and
         ($i.subtractive.failure_refs | length) == 0 then
      {valid:false, error:"failed-subtractive-missing-evidence", selected:$i.selected}
    elif $i.selected == "direct-repair" and
         $i.direct_gate_materialized != true then
      {valid:false, error:"direct-repair-gate-missing", selected:$i.selected}
    elif $i.selected != "direct-repair" and
         $i.direct_gate_materialized == true then
      {valid:false, error:"direct-gate-on-non-direct-successor", selected:$i.selected}
    else
      {valid:true, error:null, selected:$i.selected}
    end;

  .scenarios |= map(.result = evaluate) |
  .schema == "actuating-cumulative-ablation-scenarios/v1" and
  (.scenarios | length) >= 15 and
  ([.scenarios[].id] | length == (unique | length)) and
  all(.scenarios[];
    .result.valid == .expected.valid and
    .result.error == .expected.error and
    .result.selected == .expected.selected
  ) and
  ([.scenarios[] |
      select(.equivalence_group == "arrival-zero-cardinality") |
      .result.selected] | unique | length) == 1 and
  any(.scenarios[];
    .id == "duplicate-proof-owner-collapses" and
    .result.valid == true and .result.selected == "subtractive") and
  any(.scenarios[];
    .id == "required-proof-step-makes-addition-irreducible" and
    .result.valid == true and .result.selected == "direct-repair") and
  any(.scenarios[];
    .id == "passing-quotient-cannot-be-bypassed" and
    .result.error == "passing-subtractive-candidate-bypassed") and
  any(.scenarios[];
    .id == "subtractive-candidate-must-run" and
    .result.error == "subtractive-candidate-not-executed") and
  any(.scenarios[];
    .id == "subsumed-proof-machinery-collapses" and
    .result.valid == true)
' "$fixture" >/dev/null

echo "actuating cumulative ablation scenarios: pass"
