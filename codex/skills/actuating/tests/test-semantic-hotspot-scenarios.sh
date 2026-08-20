#!/bin/sh
set -eu

skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
jaq_bin=${JAQ_BIN:-jaq}
fixture="$skill_root/tests/fixtures/semantic-hotspot-scenarios.json"

"$jaq_bin" -e '
  def class_disposition:
    if (.inputs.witness_subject_recorded != true or
        .inputs.applicability_subject_recorded != true) then "blocked"
    elif .inputs.same_law == false then "split"
    elif (.inputs.current_applicability == "already-excluded" or
          .inputs.current_applicability == "not-comparable") then "not-current"
    elif (.inputs.current_applicability == "unknown" or
          .inputs.family_predicate_status == "unknown" or
          .inputs.family_claim_strength == "unknown") then "blocked"
    else "candidate"
    end;

  def theory_pressure:
    (.inputs.theory_shape as $shape |
      (["detection-shaped", "enumerative", "representation-bound"] |
       index($shape)) != null) or
    .inputs.same_law_witness_outside_phi == true or
    .inputs.material_alternative_theory_plausible == true or
    .inputs.ordinary_interpretation_adequacy == "coarse" or
    .inputs.law_distinct_behaviors_collapsed == true;

  def theory_disposition:
    if class_disposition != "candidate" then "not-applicable"
    elif (.inputs.semantic_observation_domain_status != "stated" or
          .inputs.family_theory_falsifier_status != "stated" or
          .inputs.theory_shape == "unknown" or
          .inputs.ordinary_interpretation_adequacy == "unknown" or
          .inputs.selected_interpretation_adequacy == "unknown" or
          .inputs.interpretation_adequacy_strength == "unknown" or
          .inputs.abstract_exclusion_established == "unknown" or
          .inputs.required_valid_behaviors_preserved == "unknown" or
          .inputs.required_observations_preserved == "unknown") then
      "blocked"
    elif (.inputs.selected_interpretation_adequacy == "inadequate" or
          .inputs.abstract_exclusion_established != true or
          .inputs.required_valid_behaviors_preserved != true or
          .inputs.required_observations_preserved != true) then
      "blocked"
    elif .inputs.architecture_reveals_better_theory == true then
      if (.inputs.co_refinement_used == true and
          (.inputs.architectonic_disposition as $disposition |
           (["retain", "replace", "combine", "split"] |
            index($disposition)) != null))
      then "co-refined"
      else "blocked"
      end
    elif theory_pressure then
      if .inputs.metanoetic_run != true then "blocked"
      elif .inputs.architectonic_disposition == "split" then "split"
      elif (.inputs.architectonic_disposition as $disposition |
            (["retain", "replace", "combine"] |
             index($disposition)) != null) then "adjudicated"
      else "blocked"
      end
    else "ordinary"
    end;

  def frontier_shape:
    if class_disposition == "split" or class_disposition == "not-current" then
      "none"
    elif (class_disposition == "blocked" or
          .inputs.frontier_coverage == "unknown") then
      "unresolved"
    elif .inputs.frontier_candidates > 1 then "cut"
    elif .inputs.frontier_candidates == 1 then "single"
    else "unresolved"
    end;

  def architecture_disposition:
    if class_disposition == "split" then "split"
    elif class_disposition == "not-current" then "no-current-liability"
    elif class_disposition == "blocked" or frontier_shape == "unresolved" or
         theory_disposition == "blocked" then
      "blocked"
    elif theory_disposition == "split" then "split"
    elif .inputs.external_prevention_possible == false then
      if .inputs.goal_accepts_containment == true then "contain" else "blocked" end
    elif (.inputs.architecture_claim_falsified == true or
          .inputs.owner_status != "canonical" or
          .inputs.compensating_guard_only == true or
          frontier_shape == "cut") then
      "reopen"
    elif .inputs.existing_authority_excludes_family == true then "preserve"
    else "blocked"
    end;

  def hotspot_disposition:
    if architecture_disposition == "preserve" then "realization"
    elif architecture_disposition == "reopen" then "architectural"
    elif architecture_disposition == "contain" then "contained"
    elif architecture_disposition == "split" then "false-hotspot"
    elif architecture_disposition == "blocked" then "unresolved"
    elif .inputs.current_applicability == "already-excluded" then "historical-only"
    else "unsupported-path"
    end;

  .defaults as $defaults |
  .scenarios |= map(.inputs = ($defaults * .inputs)) |
  .schema == "actuating-semantic-hotspot-scenarios/v4" and
  (.scenarios | length) >= 28 and
  ([.scenarios[].id] | length == (unique | length)) and
  all(.scenarios[];
    (.inputs.family_claim_strength as $strength |
      ["proved", "exhaustive-finite", "bounded", "property-tested",
       "sampled", "hypothesized", "unknown"] | index($strength) != null) and
    (.inputs.interpretation_adequacy_strength as $strength |
      ["proved", "exhaustive-finite", "bounded", "property-tested",
       "sampled", "hypothesized", "unknown"] | index($strength) != null) and
    (.inputs.diagnostic_exactness as $exactness |
      ["exact", "conservative-overapproximation", "bounded", "sampled",
       "unknown"] | index($exactness) != null) and
    (.inputs.owner_status as $owner |
      ["canonical", "distributed", "absent", "contested", "unknown"] |
      index($owner) != null) and
    (.inputs.current_applicability as $applicability |
      ["still-present", "transformed-applicable", "already-excluded",
       "not-comparable", "unknown"] | index($applicability) != null) and
    (.inputs.theory_shape as $shape |
      ["governing", "detection-shaped", "enumerative",
       "representation-bound", "unknown"] | index($shape) != null) and
    (.inputs.ordinary_interpretation_adequacy as $soundness |
      ["sound", "coarse", "unknown"] | index($soundness) != null) and
    (.inputs.selected_interpretation_adequacy as $soundness |
      ["sound", "inadequate", "unknown"] | index($soundness) != null) and
    (.inputs.architectonic_disposition as $disposition |
      ["not-needed", "retain", "replace", "combine", "split", "unresolved"] |
      index($disposition) != null) and
    (class_disposition == .expected.class_disposition) and
    (theory_disposition == .expected.theory_disposition) and
    (frontier_shape == .expected.frontier_shape) and
    (architecture_disposition == .expected.architecture_disposition) and
    (hotspot_disposition == .expected.hotspot_disposition)
  ) and
  ([.scenarios[].expected.theory_disposition] |
    index("ordinary") != null and
    index("adjudicated") != null and
    index("co-refined") != null and
    index("blocked") != null) and
  ([.scenarios[].expected.architecture_disposition] |
    index("preserve") != null and
    index("reopen") != null and
    index("contain") != null and
    index("blocked") != null and
    index("split") != null and
    index("no-current-liability") != null) and
  ([.scenarios[].expected.frontier_shape] |
    index("single") != null and
    index("cut") != null and
    index("unresolved") != null) and
  any(.scenarios[];
    .id == "coarse-domain-hides-invalidity" and
    .inputs.metanoetic_run == true and
    .expected.theory_disposition == "adjudicated") and
  any(.scenarios[];
    .id == "law-reflecting-quotient" and
    .expected.architecture_disposition == "preserve") and
  any(.scenarios[];
    .id == "sound-overapproximation-preserves-required-behavior" and
    .inputs.diagnostic_exactness == "conservative-overapproximation" and
    .expected.architecture_disposition == "preserve") and
  any(.scenarios[];
    .id == "unknown-diagnostic-exactness-preserves-required-behavior" and
    .inputs.diagnostic_exactness == "unknown" and
    .expected.architecture_disposition == "preserve") and
  any(.scenarios[];
    .id == "sound-overapproximation-loses-required-behavior" and
    .expected.architecture_disposition == "blocked") and
  any(.scenarios[];
    .id == "candidate-specific-erasure" and
    .expected.architecture_disposition == "blocked") and
  any(.scenarios[];
    .id == "required-observation-erasure" and
    .expected.architecture_disposition == "blocked") and
  any(.scenarios[];
    .inputs.architecture_reveals_better_theory == true and
    .inputs.co_refinement_used == true and
    .expected.theory_disposition == "co-refined") and
  any(.scenarios[];
    .inputs.architecture_reveals_better_theory == true and
    .inputs.co_refinement_used == false and
    .expected.architecture_disposition == "blocked") and
  any(.scenarios[];
    .inputs.derived_guards_required == true and
    .expected.architecture_disposition == "preserve") and
  any(.scenarios[];
    .inputs.current_applicability == "transformed-applicable" and
    .expected.architecture_disposition == "reopen")
' "$fixture" >/dev/null

echo "actuating sound-abstraction semantic-hotspot scenarios: pass"
