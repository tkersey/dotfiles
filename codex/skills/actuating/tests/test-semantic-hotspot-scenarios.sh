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
    elif class_disposition == "blocked" or frontier_shape == "unresolved" then
      "blocked"
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

  .schema == "actuating-semantic-hotspot-scenarios/v1" and
  (.scenarios | length) >= 10 and
  ([.scenarios[].id] | length == (unique | length)) and
  all(.scenarios[];
    (.inputs.family_claim_strength as $strength |
      ["proved", "exhaustive-finite", "bounded", "property-tested",
       "sampled", "hypothesized", "unknown"] | index($strength) != null) and
    (.inputs.owner_status as $owner |
      ["canonical", "distributed", "absent", "contested", "unknown"] |
      index($owner) != null) and
    (.inputs.current_applicability as $applicability |
      ["still-present", "transformed-applicable", "already-excluded",
       "not-comparable", "unknown"] | index($applicability) != null) and
    (class_disposition == .expected.class_disposition) and
    (frontier_shape == .expected.frontier_shape) and
    (architecture_disposition == .expected.architecture_disposition) and
    (hotspot_disposition == .expected.hotspot_disposition)
  ) and
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
    .inputs.derived_guards_required == true and
    .expected.architecture_disposition == "preserve") and
  any(.scenarios[];
    .inputs.current_applicability == "transformed-applicable" and
    .expected.architecture_disposition == "reopen")
' "$fixture" >/dev/null

echo "actuating semantic-hotspot scenarios: pass"
