#!/bin/sh
set -eu

skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
jaq_bin=${JAQ_BIN:-jaq}
fixture="$skill_root/tests/fixtures/construction-cycle-scenarios.json"

"$jaq_bin" -e '
  def same_claim($i):
    ($i.same_claim_finding // $i.same_family_finding // false);

  def decide($i):
    if $i.phase == "initial-review" and
       $i.material_finding == true and
       $i.semantic_barrier_complete != true
    then "continue-evidence"
    elif $i.phase == "confirmation" and $i.material_finding == true
    then "close-cut"
    elif $i.phase == "post-review" and
         $i.direct_theorem_falsifier == true
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
            $i.factorization_witness_current == true
         then "allow-reentry" else "blocked" end
    elif $i.phase == "review-entry" and $i.theorem_revoked == true
    then "blocked"
    elif $i.phase == "review-entry"
    then if $i.construction_complete == true and
            $i.proof_inventory_current == true
         then "reviewable" else "realizing" end
    elif $i.phase == "review-dispatch"
    then if $i.construction_complete == true and
            $i.proof_inventory_current == true
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

  .schema == "actuating-construction-cycle-scenarios/v1" and
  (.scenarios | length) >= 24 and
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
    .id == "isolated-restoration-when-theorem-preexists" and
    .expected == "isolated-restoration") and
  any(.scenarios[];
    .id == "stale-generator-gate-is-rejected" and
    .expected == "blocked") and
  any(.scenarios[];
    .id == "mixed-successor-routes-are-representable" and
    .expected == "mixed-successor") and
  any(.scenarios[];
    .id == "first-same-claim-successor-reopens-construction" and
    .expected == "construction-normalization") and
  any(.scenarios[];
    .id == "second-same-claim-successor-revokes-unchanged-theorem" and
    .expected == "theorem-rederive-required") and
  any(.scenarios[];
    .id == "direct-theorem-falsifier-revokes-immediately" and
    .expected == "theorem-rederive-required") and
  any(.scenarios[];
    .id == "same-law-different-family-does-not-increment-recurrence" and
    .expected == "construction-normalization") and
  any(.scenarios[];
    .id == "revoked-theorem-blocks-third-candidate" and
    .expected == "blocked") and
  any(.scenarios[];
    .id == "material-theorem-delta-and-factorization-allow-reentry" and
    .expected == "allow-reentry")
' "$fixture" >/dev/null

echo "actuating construction cycle scenarios: pass"
