#!/bin/sh
set -eu

skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
jaq_bin=${JAQ_BIN:-jaq}
fixture="$skill_root/tests/fixtures/construction-cycle-scenarios.json"

"$jaq_bin" -e '
  def same_claim($i):
    ($i.same_claim_finding // $i.same_family_finding // false);

  def source_closed($i):
    $i.source_topology_derived == true and
    $i.topology_authority_bound == true and
    $i.exact_head_topology_rederived == true and
    $i.topology_transformation_proved == true and
    $i.factorization_domain_total == true and
    $i.cut_domination_complete == true and
    $i.residuals_owned == true and
    $i.model_authored_only != true;

  def bounded_closed($i):
    (($i.claim_strength // "") == "bounded" or
     ($i.claim_strength // "") == "contained") and
    $i.claim_strength_explicit == true and
    $i.bounded_domain_explicit == true and
    $i.residuals_owned == true;

  def review_ready($i):
    $i.construction_complete == true and
    $i.proof_inventory_current == true and
    (source_closed($i) or bounded_closed($i));

  def local_premise($i):
    (["realization", "proof", "generated-output", "artifact-binding"] |
      index($i.earliest_failed_premise // "")) != null;

  def semantic_premise($i):
    (["comparison-domain", "invalid-family", "semantic-interpretation",
      "semantic-equivalence", "source-topology", "canonical-owner",
      "carrier-or-invariant", "constructor-or-representation",
      "legal-transition", "producer-factorization",
      "admission-path-domination", "bypass-closure",
      "required-valid-preservation"] |
      index($i.earliest_failed_premise // "")) != null;

  def theorem_localized($i):
    $i.positive_claim_falsified == true and
    (($i.earliest_failed_premise // "") != "") and
    $i.source_bound_predecessor_theorem_projected == true and
    (($i.exact_predecessor_theorem_reprovable | type) == "boolean");

  def decide_selection($i):
    if $i.semantic_barrier_complete != true or
       $i.basis_complete != true or
       ($i.live_owner_sources_complete? == false)
    then "blocked"
    elif ($i.law_authority // "entailed") == "new-requirement" or
         ($i.law_authority // "entailed") == "underdetermined"
    then "authority-required"
    elif ($i.counterexample_accepted // true) != true or
         (["already-excluded", "not-comparable"] |
           index($i.applicability_status // "still-present")) != null
    then "no-current-liability"
    elif theorem_localized($i) != true
    then "blocked"
    elif $i.explicit_deferral_requested == true
    then if $i.deferral_authorized == true and
            $i.closure_consequence_explicit == true
         then "explicitly-deferred" else "blocked" end
    elif ($i.earliest_failed_premise // "") == "claim-strength"
    then if $i.weaker_claim_explicit == true and
            $i.claim_narrowing_authorized == true and
            $i.closure_consequence_explicit == true
         then "claim-narrowing-or-containment" else "blocked" end
    elif $i.exact_predecessor_theorem_reprovable == true and local_premise($i)
    then if $i.direct_gate_valid == true
         then "isolated-restoration" else "blocked" end
    elif $i.exact_predecessor_theorem_reprovable == false and
         $i.semantic_premise_falsified == true and semantic_premise($i)
    then "construction-normalization"
    else "blocked"
    end;

  def decide($i):
    if $i.phase == "initial-review" and
       $i.material_finding == true and
       $i.semantic_barrier_complete != true
    then "continue-evidence"
    elif $i.phase == "confirmation" and $i.material_finding == true
    then "close-cut"
    elif $i.phase == "universalist-entry"
    then if $i.topology_authority_bound == true and
            $i.model_authored_only != true and
            ($i.source_topology_derived == true or
             $i.open_domain_generator == true)
         then "allow-universalist" else "blocked" end
    elif $i.phase == "post-review" and
         ($i.direct_theorem_falsifier == true or
          $i.unmodeled_sanctioned_topology_element == true)
    then "theorem-rederive-required"
    elif $i.phase == "post-review" and
         same_claim($i) == true and
         $i.theorem_materially_changed != true and
         (($i.prior_same_claim_successor_invalidations // 0) >= 1)
    then "theorem-rederive-required"
    elif $i.phase == "post-review" and
         (same_claim($i) == true or $i.same_law_finding == true)
    then "theorem-response-required"
    elif $i.phase == "theorem-reentry"
    then if $i.theorem_revoked == true and
            $i.theorem_materially_changed == true and
            $i.source_topology_complete == true and
            $i.exact_head_topology_rederived == true and
            $i.topology_transformation_proved == true and
            $i.factorization_witness_current == true
         then "allow-reentry" else "blocked" end
    elif $i.phase == "review-entry" and $i.theorem_revoked == true
    then "blocked"
    elif $i.phase == "review-entry"
    then if review_ready($i)
         then "reviewable" else "realizing" end
    elif $i.phase == "review-dispatch"
    then if review_ready($i)
         then "allow-review" else "blocked" end
    elif $i.phase == "gate"
    then if $i.duplicate_gate == true
         then "blocked"
         elif $i.gate_head == $i.current_head
         then "admit-gate"
         else "blocked"
         end
    elif $i.phase == "route-set"
    then if (($i.routes | sort) ==
             (["construction-normalization", "isolated-restoration"] | sort))
         then "mixed-successor" else "blocked" end
    elif $i.phase == "selection"
    then decide_selection($i)
    else "blocked"
    end;

  .schema == "actuating-construction-cycle-scenarios/v3" and
  (.scenarios | length) >= 42 and
  ([.scenarios[].id] | length == (unique | length)) and
  all(.scenarios[]; decide(.input) == .expected) and
  ([.scenarios[] |
      select(.equivalence_group == "arrival-order") |
      .expected] | unique | length) == 1 and
  any(.scenarios[];
    .id == "live-provider-source-missing-blocks-selection" and
    .expected == "blocked") and
  any(.scenarios[];
    .id == "high-severity-realization-defect-restores" and
    .expected == "isolated-restoration") and
  any(.scenarios[];
    .id == "low-severity-owner-defect-normalizes" and
    .expected == "construction-normalization") and
  any(.scenarios[];
    .id == "unreachable-witness-has-no-current-liability" and
    .expected == "no-current-liability") and
  any(.scenarios[];
    .id == "new-requirement-needs-authority" and
    .expected == "authority-required") and
  any(.scenarios[];
    .id == "authorized-claim-overstatement-narrows" and
    .expected == "claim-narrowing-or-containment") and
  any(.scenarios[];
    .id == "failed-restoration-gate-does-not-normalize" and
    .expected == "blocked") and
  any(.scenarios[];
    .id == "unknown-theorem-relation-does-not-normalize" and
    .expected == "blocked") and
  any(.scenarios[];
    .id == "authorized-liability-deferral-is-explicit" and
    .expected == "explicitly-deferred") and
  any(.scenarios[];
    .id == "first-same-claim-successor-reopens-construction" and
    .expected == "theorem-response-required") and
  any(.scenarios[];
    .id == "second-same-claim-successor-revokes-unchanged-theorem" and
    .expected == "theorem-rederive-required") and
  any(.scenarios[];
    .id == "unmodeled-sanctioned-path-revokes-topology-immediately" and
    .expected == "theorem-rederive-required") and
  any(.scenarios[];
    .id == "self-authored-omission-list-is-not-reviewable" and
    .expected == "realizing") and
  any(.scenarios[];
    .id == "source-derived-total-factorization-is-reviewable" and
    .expected == "reviewable") and
  any(.scenarios[];
    .id == "bounded-claim-with-explicit-residuals-is-reviewable" and
    .expected == "reviewable") and
  any(.scenarios[];
    .id == "material-theorem-delta-and-factorization-allow-reentry" and
    .expected == "allow-reentry")
' "$fixture" >/dev/null

echo "actuating theorem-directed construction cycle scenarios: pass"
