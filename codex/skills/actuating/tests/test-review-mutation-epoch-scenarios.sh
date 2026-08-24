#!/bin/sh
set -eu

skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
jaq_bin=${JAQ_BIN:-jaq}
fixture="$skill_root/tests/fixtures/review-mutation-epoch-scenarios.json"

"$jaq_bin" -e '
  def sibling_complete:
    (.inputs.sibling_disposition as $v |
      ["passed", "exhaustive", "not-meaningful"] | index($v) != null);

  def recurrence_requires_reconsideration:
    .inputs.same_generator_recurrence == true and
    .inputs.separation_proof != true and
    (.inputs.proposed_member_enumeration == true or
     .inputs.generative_family_evidence != true);

  def epoch_ready:
    .inputs.material_finding == true and
    .inputs.required_terminal_barrier_complete == true and
    .inputs.all_applicable_classes_folded == true and
    .inputs.causal_basis_complete == true and
    sibling_complete and
    .inputs.selected_target_stated == true and
    recurrence_requires_reconsideration != true;

  def phase:
    if .inputs.material_finding != true then "review"
    elif .inputs.required_terminal_barrier_complete != true then "await-barrier"
    elif recurrence_requires_reconsideration then "reconsider-architecture"
    elif epoch_ready != true then "reconcile"
    elif .inputs.direct_repair_selected == true and
         .inputs.direct_repair_gate_materialized != true then "await-direct-gate"
    elif .inputs.selected_target_completely_realized != true or
         .inputs.strongest_validation_passed != true then "realize"
    else "redispatch-ready"
    end;

  def mutation:
    if epoch_ready != true then "forbidden"
    elif .inputs.direct_repair_selected == true and
         .inputs.direct_repair_gate_materialized != true then "forbidden"
    elif .inputs.selected_target_completely_realized == true then "complete"
    else "epoch-target"
    end;

  def redispatch:
    if phase == "review" then "continue-current"
    elif phase == "redispatch-ready" then "restart-selected-schedule"
    else "forbidden"
    end;

  def direct_gate_scope:
    if .inputs.direct_repair_selected != true then "not-applicable"
    elif epoch_ready != true then "forbidden"
    else "complete-epoch-target"
    end;

  .defaults as $defaults |
  .scenarios |= map(.inputs = ($defaults * .inputs)) |
  .schema == "actuating-review-mutation-epoch-scenarios/v1" and
  (.scenarios | length) >= 12 and
  ([.scenarios[].id] | length == (unique | length)) and
  all(.scenarios[];
    (.inputs.schedule as $v |
      ["parallel", "serial", "confirmation"] | index($v) != null) and
    (.inputs.sibling_disposition as $v |
      ["passed", "exhaustive", "not-meaningful", "missing", "failed"] |
      index($v) != null) and
    phase == .expected.phase and
    mutation == .expected.mutation and
    redispatch == .expected.redispatch and
    direct_gate_scope == .expected.direct_gate_scope
  ) and
  any(.scenarios[];
    .id == "parallel-material-finding-waits-for-barrier" and
    .expected.phase == "await-barrier") and
  any(.scenarios[];
    .id == "confirmation-finding-exits-convergence" and
    .expected.redispatch == "forbidden") and
  any(.scenarios[];
    .id == "complete-direct-repair-epoch" and
    .expected.mutation == "epoch-target" and
    .expected.direct_gate_scope == "complete-epoch-target") and
  any(.scenarios[];
    .id == "realized-epoch-restarts-once" and
    .expected.phase == "redispatch-ready") and
  any(.scenarios[];
    .id == "same-generator-member-enumeration-reopens-architecture" and
    .expected.phase == "reconsider-architecture") and
  any(.scenarios[];
    .id == "same-generator-without-family-evidence-reopens-architecture" and
    .expected.phase == "reconsider-architecture") and
  any(.scenarios[];
    .id == "same-generator-generative-repair" and
    .expected.mutation == "epoch-target")
' "$fixture" >/dev/null

echo "actuating review-mutation reconciliation epoch scenarios: pass"
