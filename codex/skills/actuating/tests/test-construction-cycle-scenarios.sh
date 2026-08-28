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
    elif $i.phase == "post-review" and same_claim($i) == true
    then "construction-normalization"
    elif $i.phase == "post-review" and $i.same_law_finding == true
    then "construction-normalization"
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
    elif $i.phase == "selection" and
         $i.semantic_barrier_complete != true
    then "blocked"
    elif $i.phase == "selection" and
         $i.basis_complete != true
    then "blocked"
    elif $i.phase == "selection" and
         $i.carrier_already_complete == true and
         $i.producer_factorization_complete == true and
         $i.bypasses_closed == true and
         $i.realization_defect_only == true
    then if $i.direct_gate_valid == true
         then "isolated-restoration" else "blocked" end
    elif $i.phase == "selection"
    then "construction-normalization"
    else "blocked"
    end;

  .schema == "actuating-construction-cycle-scenarios/v2" and
  (.scenarios | length) >= 32 and
  ([.scenarios[].id] | length == (unique | length)) and
  all(.scenarios[]; decide(.input) == .expected) and
  ([.scenarios[] |
      select(.equivalence_group == "arrival-order") |
      .expected] | unique | length) == 1 and
  any(.scenarios[];
    .id == "serial-material-finding-completes-initial-wave" and
    .expected == "continue-evidence") and
  any(.scenarios[];
    .id == "parallel-recovery-remains-in-semantic-barrier" and
    .expected == "continue-evidence") and
  any(.scenarios[];
    .id == "source-derived-topology-allows-universalist" and
    .expected == "allow-universalist") and
  any(.scenarios[];
    .id == "model-authored-path-list-blocks-universalist" and
    .expected == "blocked") and
  any(.scenarios[];
    .id == "isolated-restoration-when-theorem-preexists" and
    .expected == "isolated-restoration") and
  any(.scenarios[];
    .id == "stale-generator-gate-is-rejected" and
    .expected == "blocked") and
  any(.scenarios[];
    .id == "mixed-successor-routes-are-representable" and
    .expected == "mixed-successor") and
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
    .id == "successor-topology-mismatch-is-not-reviewable" and
    .expected == "realizing") and
  any(.scenarios[];
    .id == "material-theorem-delta-and-factorization-allow-reentry" and
    .expected == "allow-reentry")
' "$fixture" >/dev/null

echo "actuating construction cycle scenarios: pass"
