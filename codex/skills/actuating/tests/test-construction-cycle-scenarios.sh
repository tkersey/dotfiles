#!/bin/sh
set -eu

skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
jaq_bin=${JAQ_BIN:-jaq}
fixture="$skill_root/tests/fixtures/construction-cycle-scenarios.json"

"$jaq_bin" -e '
  def decide($i):
    if $i.phase == "initial-review" and
       $i.material_finding == true and
       $i.semantic_barrier_complete != true
    then "continue-evidence"
    elif $i.phase == "confirmation" and $i.material_finding == true
    then "close-cut"
    elif $i.phase == "post-review" and
         $i.same_family_finding == true and
         $i.separation_proof != true
    then "construction-normalization"
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
  (.scenarios | length) >= 18 and
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
    .id == "same-family-successor-reopens-construction" and
    .expected == "construction-normalization")
' "$fixture" >/dev/null

echo "actuating construction cycle scenarios: pass"
