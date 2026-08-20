#!/bin/sh
set -eu

skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
jaq_bin=${JAQ_BIN:-jaq}
fixture="$skill_root/tests/fixtures/post-elimination-scenarios.json"

"$jaq_bin" -e '
  def authority:
    if .inputs.current_applicable != true then "not-current"
    elif .inputs.law_authority == "entailed" then "counterexample"
    elif .inputs.law_authority == "strengthening" then "follow-up"
    elif .inputs.law_authority == "preference" then "rejected"
    elif .inputs.law_authority == "new-requirement" then "reopen-goal"
    else "blocked"
    end;

  def lease:
    if .inputs.prior_eliminated != true or .inputs.same_law != true or
       .inputs.current_applicable != true then
      "not-applicable"
    elif authority != "counterexample" then
      "non-authoritative"
    elif .inputs.validity_horizon_relation == "outside" or
         .inputs.claim_family_relation == "different-family" then
      "not-applicable"
    elif .inputs.validity_horizon_relation == "unknown" or
         .inputs.claim_family_relation == "unknown" then
      "unresolved"
    elif .inputs.premise_failure == "realization" or
         .inputs.premise_failure == "proof" then
      if .inputs.witness_within_phi == true and
         .inputs.path_already_covered == true and
         .inputs.interpretation_reflects_witness == true
      then "retain-theory-reprove"
      else "unresolved"
      end
    elif .inputs.premise_failure == "theory" then "revise-theory"
    elif .inputs.premise_failure == "theory-split" then "split-theory"
    elif .inputs.premise_failure == "admission" then "revise-admission"
    elif .inputs.premise_failure == "interpretation" then "revise-interpretation"
    elif .inputs.premise_failure == "owner" then "revise-owner"
    elif .inputs.premise_failure == "authority" then "reopen-goal"
    else "unresolved"
    end;

  def next_action:
    if authority == "not-current" then "reject-current-liability"
    elif authority == "follow-up" then "non-blocking-follow-up"
    elif authority == "rejected" then "reject-finding"
    elif authority == "reopen-goal" then "reopen-goal"
    elif authority == "blocked" then "seek-authority"
    elif lease == "not-applicable" then "normal-reconciliation"
    elif lease == "retain-theory-reprove" and
         .inputs.premise_failure == "realization" then "repair-realization"
    elif lease == "retain-theory-reprove" then "rebuild-proof"
    elif lease == "reopen-goal" then "reopen-goal"
    elif (lease | startswith("revise-")) or lease == "split-theory" then
      "recompile-theory"
    else "blocked"
    end;

  def reissue:
    if .inputs.reissue_attempted != true then "not-applicable"
    elif authority != "counterexample" then "ineligible"
    elif lease == "unresolved" or lease == "non-authoritative" or
         lease == "not-applicable" or lease == "reopen-goal" then "ineligible"
    elif .inputs.successor_theory_restated != true or
         .inputs.family_level_proof != true or
         .inputs.repaired_examples_only == true then "ineligible"
    elif .inputs.sibling_prediction_status == "exhaustive" and
         .inputs.sibling_probes_passed == true then "eligible"
    elif .inputs.sibling_prediction_status == "stated" and
         .inputs.sibling_probes_passed == true then "eligible"
    else "ineligible"
    end;

  .defaults as $defaults |
  .scenarios |= map(.inputs = ($defaults * .inputs)) |
  .schema == "actuating-post-elimination-scenarios/v2" and
  (.scenarios | length) >= 20 and
  ([.scenarios[].id] | length == (unique | length)) and
  all(.scenarios[];
    (.inputs.law_authority as $v |
      ["entailed", "strengthening", "preference", "new-requirement",
       "underdetermined"] | index($v) != null) and
    (.inputs.premise_failure as $v |
      ["none", "realization", "proof", "theory", "theory-split",
       "admission", "interpretation", "owner", "authority", "unknown"] |
      index($v) != null) and
    (.inputs.claim_family_relation as $v |
      ["falsifies-claim", "different-family", "unknown"] |
      index($v) != null) and
    (.inputs.validity_horizon_relation as $v |
      ["inside", "outside", "unknown"] | index($v) != null) and
    (.inputs.sibling_prediction_status as $v |
      ["stated", "exhaustive", "absent", "unknown"] | index($v) != null) and
    authority == .expected.authority and
    lease == .expected.lease and
    next_action == .expected.next and
    reissue == .expected.reissue
  ) and
  any(.scenarios[];
    .id == "post-elimination-realization-failure" and
    .expected.lease == "retain-theory-reprove") and
  any(.scenarios[];
    .id == "post-elimination-witness-outside-phi" and
    .expected.lease == "revise-theory") and
  any(.scenarios[];
    .id == "post-elimination-unknown-premise" and
    .expected.next == "blocked") and
  any(.scenarios[];
    .id == "unchanged-theory-repaired-examples-only" and
    .expected.reissue == "ineligible") and
  any(.scenarios[];
    .id == "successor-theory-predicts-siblings" and
    .expected.reissue == "eligible") and
  any(.scenarios[];
    .id == "strengthening-after-elimination" and
    .expected.lease == "non-authoritative") and
  any(.scenarios[];
    .id == "same-law-different-family" and
    .expected.lease == "not-applicable") and
  any(.scenarios[];
    .id == "outside-validity-horizon" and
    .expected.lease == "not-applicable") and
  any(.scenarios[];
    .id == "unknown-validity-horizon" and
    .expected.lease == "unresolved") and
  any(.scenarios[];
    .id == "reopened-authority-cannot-reissue" and
    .expected.reissue == "ineligible")
' "$fixture" >/dev/null

echo "actuating post-elimination scenarios: pass"
