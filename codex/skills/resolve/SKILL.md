---
name: resolve
description: "Resolve the current branch through a CAS-first Review Governor with a mutation-permit interlock after same-cluster recurrence. Use for `$resolve`, branch resolution, review/fix/validate/commit/push loops, PR sweep, three consecutive clean reviews, review_governor_record / RGR-v2, RGR-V2-MUTATION-PERMIT, same-cluster local-patching disablement, positive production net embargo, owner coarseness gate, proof matrix gate, negative-ledger operational evidence, boundary inventory/universalist trigger, governor compliance reporting, and material-improvement scoring. Do not use for one-shot review, PR creation only, merging/landing, isolated adjudication, or final closure proof without branch mutation."
---

# resolve

## Purpose

Resolve the current branch to a pinned-review-clean, validated, committed, pushed, and PR-comment-swept state without letting review feedback directly actuate unbounded code growth.

`$resolve` is a **Review Governor**.

```text
Reviews sense. The governor decides. Implementation obeys.
```

This version adds the missing operational interlock:

```text
After same-cluster recurrence, no production mutation without an explicit RGR-V2-MUTATION-PERMIT.
```

The governor must choose collapse, normal form, distillation, boundary clarification, or blocked. It may not keep adding validation/replay/evidence branches to an already-growing owner just because the owner is "existing."

## Core doctrine

```text
Do not satisfy the reviewer. Govern the feedback loop.
Review findings are counterexamples, not tasks.
Existing-owner mutation is necessary but not sufficient.
After the second same-cluster finding, local patching is disabled.
After same-cluster recurrence, positive production net is embargoed.
After same-cluster recurrence, production mutation requires RGR-V2-MUTATION-PERMIT.
Same coarse owner + growing branches means owner coarseness must be adjudicated.
Negative-ledger must be operationally evidenced, not asserted.
Universalist/boundary inventory is required when the same owner keeps absorbing semantic branches.
Tests must become a proof matrix, not a wound catalog.
No governor-compliance metrics, no improvement claim.
```

## Activation Kernel

Use `$resolve` when the user wants the current branch driven through review/fix/validate/push/PR-sweep closure.

Do not use `$resolve` when:

- the user wants a one-shot review only;
- the user wants PR creation or proof publication only; use `$ship`;
- the user wants merge, checks-watch, or cleanup; use `$land`;
- the user wants actionability only; use `$review-adjudication`;
- the user wants final readiness only; use `$verification-closure`;
- the user wants implementation of an already selected route only; use `$fixed-point-driver` or `$accretive-implementer`.

Default mode: **CAS-first full branch resolution**.

Root owns branch mutation, review streak, base/head pins, route selection, commits, pushes, PR thread decisions, and completion. Workers and companions are advisory unless explicitly given a bounded handoff.

## Completion bar

```text
3 consecutive clean reviews
+ pinned backend/base/head/fingerprint
+ full validation pass
+ intended commit/push
+ complete post-push PR sweep
+ no actionable PR comments remaining
+ no open same-cluster governor gate
+ no active negative exclusion against selected route
+ no owner-coarseness gate left unknown after recurrence
+ no positive production net after recurrence unless explicitly warranted
+ no same-cluster post-recurrence mutation without RGR-V2-MUTATION-PERMIT
+ no one-test-per-wound proof growth without matrix justification
+ review_governor_record emitted for finding-bearing waves
+ governor-compliance metrics reported
+ material-improvement score reported
```

## Backend selection

`$resolve` is CAS-first. Native review is fallback-only after recorded CAS failure or explicit user request.

Do not run naked `codex review --base main`.

Review results must pin:

- backend class;
- base ref;
- base SHA;
- `HEAD` SHA;
- target fingerprint when available.

Switching backend, base, head, or fingerprint resets the clean-review streak.

## Review Governor loop

Repeat until `clean_review_streak == 3`:

1. **Sense**
   - Run selected review driver.
   - Normalize CAS/native/PR/validation findings into sensor inputs.
   - Separate observed facts, review claims, proposed changes, and uncertainty.

2. **Estimate state**
   - Cluster findings before editing.
   - Track same-cluster count and findings after first fix.
   - Track owner growth, validation/evidence branch growth, and test-growth shape.
   - Estimate review entropy.
   - Classify system context when repeated events imply structure.

3. **Govern**
   - Enumerate candidate routes.
   - Disable local patching after same-cluster recurrence.
   - Enforce positive production net embargo when recurrence occurs.
   - Run owner coarseness gate when the same owner keeps growing.
   - Run negative-ledger operational check before repeating routes.
   - Run boundary inventory / universalist check when repeated owner growth suggests missing semantic surface.
   - Select the lowest-surface entropy-reducing route.
   - Emit `RGR-V2-MUTATION-PERMIT` before mutation when required.

4. **Actuate**
   - Hand off only the permitted selected route to `$fixed-point-driver` / `$accretive-implementer`.
   - Preserve forbidden actions, proof matrix, and surface budget.
   - Do not mutate if permit is missing or `handoff_allowed: no`.

5. **Observe**
   - Run targeted proof.
   - Update surface delta, proof matrix, and cluster trajectory.
   - Commit coherent green slices only when safe.
   - Restart review on the current tuple.

6. **Learn**
   - Capture route failures as negative evidence.
   - Update governor-compliance, decision-impact, and material-improvement metrics.
   - Carry recommendation outcomes into the final report.

## Review entropy

Review entropy is the system's tendency to keep generating unresolved or adjacent review findings.

Track:

```yaml
review_entropy:
  unresolved_counterexample_families:
  same_cluster_recurrence:
  production_surface_growth:
  helper_wrapper_adapter_growth:
  public_surface_growth:
  fallback_or_compatibility_growth:
  validation_branch_growth:
  evidence_predicate_growth:
  proof_matrix_sprawl:
  repeated_failed_route_penalty:
  delayed_feedback_risk:
```

A patch is allowed only when the selected route reduces review entropy better than the alternatives.

Ask:

```text
Does this reduce the system's tendency to generate this class of review findings?
```

Not merely:

```text
Does this silence this comment?
```

## Same-cluster governor rule

A cluster is a group of review, validation, or PR findings sharing a subsystem, owner, state machine, protocol, authority boundary, parser/validator, lifecycle, proof surface, or invariant family.

If a second finding appears in the same cluster during one `$resolve` run:

```text
ordinary local patching is disabled
```

Allowed routes after the governor rule fires:

1. `no-change`
2. `validate-only`
3. `delete-collapse-canonicalize`
4. `normal-form-decision`
5. `review-distillation-mode`
6. `boundary-redesign`
7. `blocked`

`mutate-existing-owner` is **not selectable** after recurrence. It may appear only as the implementation detail of `normal-form-decision`, and only when the governor record proves:

- the owner is not too coarse;
- delete/collapse is insufficient;
- the change removes/collapses more semantic surface than it adds, or positive growth is explicitly warranted;
- this is not another local point fix;
- the proof matrix covers the family.

`add-new-surface` is not a normal route. It is a capital expenditure. It requires explicit expansion warrant, paid abstraction rent, boundary inventory, and proof that lower-surface routes cannot satisfy the counterexample family.

## Mutation Permit Interlock

After same-cluster recurrence, **no production mutation may occur** unless the immediately preceding assistant decision emits the literal key:

```yaml
RGR-V2-MUTATION-PERMIT:
```

This is stronger than "emit a review_governor_record somewhere." The permit is the actuator interlock.

Required shape:

```yaml
RGR-V2-MUTATION-PERMIT:
  permit_version: RGR-MP-v1
  artifact_state:
    branch: "..."
    base_sha: "..."
    head_sha: "..."
    review_backend: cas-lane | native-cli | cas-native-fallback | none
    target_fingerprint: "..."
  cluster_id: "..."
  same_cluster_count: 2
  selected_route: delete-collapse-canonicalize | normal-form-decision | review-distillation-mode | boundary-redesign | blocked
  mutate_existing_owner_as_implementation_detail: yes | no
  production_embargo:
    required: yes
    expected_production_net: negative | zero | positive | unknown
    positive_net_warrant: none | retires-more-surface | uninhabitable-state | explicit-expansion | distillation | boundary-redesign
  owner_coarseness_gate:
    owner: "..."
    owner_too_coarse: yes | no | unknown
    decision: continue_owner | split_boundary | universalist_check | reduce_surface | distill | blocked
  boundary_inventory:
    required: yes | no
    missing_boundary_artifact: yes | no | unknown
    decision: universalist | reduce | normal-form | distill | blocked
  negative_route_gate:
    query_or_map: yes | no
    ledger_cli: ledger
    store: ".ledger/negative-ledger.jsonl"
    command: "ledger map --route ... --cluster ... --artifact ..."
    exit_code: 0 | 2 | 3
    ledger_available: yes | no
    active_exclusion_match: yes | no
    exclusion_id: "none | NEG-..."
    fuzzy_candidates: 0
    fuzzy_authority: suggest_only | none
    failure: none | ledger_missing
    route_changed_by_exclusion: yes | no
    capture_created: yes | no
  proof_matrix_gate:
    family_matrix_present: yes | no
    one_test_per_wound: yes | no
    tests_retired_or_merged: []
  forbidden_actions: []
  permitted_scope: []
  handoff_allowed: yes | no
```

Hard rules:

- If `same_cluster_count >= 2`, permit is required before any `apply_patch`, file edit, or production-affecting mutation.
- If `selected_route` is `mutate-existing-owner`, permit is invalid.
- If `mutate_existing_owner_as_implementation_detail: yes`, `selected_route` must be `normal-form-decision`.
- If `expected_production_net: positive`, `positive_net_warrant` cannot be `none`.
- If `owner_too_coarse: yes | unknown`, `decision` cannot be `continue_owner`.
- If `negative_route_gate.query_or_map: no`, `ledger_available: no`, or `exit_code: 3`, permit is invalid.
- If `proof_matrix_gate.one_test_per_wound: yes` and `family_matrix_present: no`, permit is invalid.
- If `handoff_allowed: no`, mutation is blocked.

## Positive Production Net Embargo

After same-cluster recurrence:

```text
production_net must be <= 0
```

unless one of these is true:

- the patch retires or collapses more semantic surface than it adds;
- the patch makes an illegal state uninhabitable at the right boundary;
- the user/upstream authority explicitly accepts expansion;
- review-distillation or boundary redesign proves positive net is the lowest total-system-surface route.

Allowed after recurrence:

- delete/collapse;
- canonicalize duplicated predicates;
- replace several branches with one existing table/model;
- move logic to a clearer existing seam while deleting old branches;
- make an impossible state unrepresentable;
- distill tests into a family matrix.

Blocked by default after recurrence:

- add one more validation branch;
- add one more evidence predicate;
- add one more fallback/compatibility case;
- add one more focused regression for one wound;
- grow a coarse owner without owner-coarseness adjudication.

## Owner Coarseness Gate

Required when any trigger is true:

```yaml
owner_coarseness_gate:
  required: yes | no
  trigger:
    same_cluster_count_gte_2: yes | no
    same_file_repeated_growth: yes | no
    same_owner_repeated_mutation: yes | no
    validation_branch_growth: yes | no
    evidence_predicate_growth: yes | no
    compatibility_or_version_branch_growth: yes | no
  owner: "..."
  owner_too_coarse: yes | no | unknown
  decision:
    route: continue_owner | split_boundary | universalist_check | reduce_surface | distill | blocked
  reason: "..."
```

Hard rule:

```text
If owner_too_coarse is yes or unknown after same-cluster recurrence,
do not add another validation/replay/evidence branch to that owner.
```

`continue_owner` is allowed only when the owner is proven to be the correct semantic unit and the change is surface-neutral or surface-reducing.

## Boundary inventory / universalist trigger

Do not require `$universalist` for every repeated cluster. Do require a boundary inventory when the same owner keeps absorbing semantic branches.

Trigger when:

- same cluster recurs;
- same coarse owner keeps growing;
- validation/replay/evidence branches accumulate;
- compatibility/version semantics keep appearing;
- receipt/journal/replay/authority semantics are spread across parallel predicates;
- public/internal semantics are repeatedly reviewed.

Minimum boundary inventory:

```yaml
boundary_inventory:
  required: yes | no
  semantic_surfaces: []
  duplicated_or_parallel_predicates: []
  implicit_table_or_algebra: yes | no | unknown
  missing_boundary_artifact: yes | no | unknown
  decision: universalist | reduce | normal-form | distill | blocked
  reason: "..."
```

If `missing_boundary_artifact: yes | unknown` after recurrence, do not continue ordinary owner mutation. Route to `$universalist`, `$reduce`, distillation, or block.

## Negative-ledger operational evidence

Do not merely write:

```text
negative_route_gate: checked
```

The gate must show evidence:

```yaml
negative_route_gate:
  checked: yes | no
  evidence_source:
    skill_read: yes | no
    query_or_map: yes | no
    ledger_cli: ledger
    store: ".ledger/negative-ledger.jsonl"
    command: "ledger map --route ... --cluster ... --artifact ..."
    exit_code: 0 | 2 | 3
    ledger_available: yes | no
    prior_route_search_terms: []
    current_cluster_compared_to_prior: yes | no
  active_exclusion_match: yes | no | null
  exclusion_id: "none | NEG-..."
  fuzzy_candidates: 0
  fuzzy_authority: suggest_only | none
  failure: none | ledger_missing
  route_changed_by_exclusion: yes | no
  capture_created: yes | no
  handoff_allowed: yes | no
```

Hard rule:

```text
If same_cluster_count >= 2 and query_or_map is no, `ledger map` is missing, `ledger_available: no`, or `exit_code: 3`, mutation is blocked.
```

Same-cluster recurrence after a selected route creates a negative-evidence capture candidate unless proven unrelated, stale, or superseded.

## Proof Matrix Gate

After same-cluster recurrence, tests must prove the counterexample family, not just the latest wound.

```yaml
proof_matrix_gate:
  required: yes | no
  one_test_per_wound: yes | no
  family_matrix_present: yes | no
  duplicate_fixture_cases: yes | no
  tests_retired_or_merged: []
  allowed: yes | no
  reason: "..."
```

Hard rule:

```text
If the new test only encodes the latest wound and does not expand or compact a family matrix, block or justify explicitly.
```

Prefer:

- table-driven cases;
- invariant matrix;
- authority-boundary matrix;
- version/compatibility matrix with strict current-format guard;
- existing test extension over a new bespoke test;
- retiring/merging duplicate wound tests.

## Review Governor Record

Every finding-bearing review wave and every same-cluster governor decision must emit or update:

```yaml
review_governor_record:
  record_version: RGR-v2
  resolve_run_id: "..."
  artifact_state:
    branch: "..."
    base_sha: "..."
    head_sha: "..."
    review_backend: cas-lane | native-cli | cas-native-fallback | none
    target_fingerprint: "..."
  sensor_input:
    findings:
      - id: "..."
        source: cas | native_review | pr_comment | validation | user
        cluster_id: "..."
        evidence_discipline:
          observed_fact: "..."
          review_claim: "..."
          proposed_change: "..."
          uncertainty: "..."
          scope_basis: "..."
  state_estimate:
    cluster_id: "..."
    same_cluster_count: 0
    findings_after_first_fix: 0
    counterexample_family: "..."
    recurring_owner: "..."
    recurring_file: "..."
    system_type: clear | complicated | complex | chaotic | mixed | unknown
    feedback_loop: "..."
    delayed_feedback: yes | no | unknown
    local_vs_whole_tradeoff: yes | no | unknown
    review_entropy:
      same_cluster_recurrence: 0
      production_surface_growth: 0
      helper_wrapper_adapter_growth: 0
      public_surface_growth: 0
      fallback_or_compatibility_growth: 0
      validation_branch_growth: 0
      evidence_predicate_growth: 0
      proof_matrix_sprawl: 0
      repeated_failed_route_penalty: 0
  owner_coarseness_gate:
    required: yes | no
    owner_too_coarse: yes | no | unknown
    decision:
      route: continue_owner | split_boundary | universalist_check | reduce_surface | distill | blocked
      reason: "..."
  boundary_inventory:
    required: yes | no
    semantic_surfaces: []
    duplicated_or_parallel_predicates: []
    implicit_table_or_algebra: yes | no | unknown
    missing_boundary_artifact: yes | no | unknown
    decision: universalist | reduce | normal-form | distill | blocked
  candidate_routes:
    - route: no-change | validate-only | delete-collapse-canonicalize | normal-form-decision | review-distillation-mode | boundary-redesign | blocked
      counterexamples_covered: []
      production_surface_delta: negative | zero | bounded-positive | expansion | unknown
      semantic_surface_retired: []
      proof_cost: low | medium | high | unknown
      recurrence_risk: low | medium | high | unknown
      rejected_because: "..."
  negative_memory:
    checked: yes | no
    evidence_source:
      skill_read: yes | no
      query_or_map: yes | no
      ledger_cli: ledger
      store: ".ledger/negative-ledger.jsonl"
      command: "ledger map --route ... --cluster ... --artifact ..."
      exit_code: 0 | 2 | 3
      ledger_available: yes | no
      prior_route_search_terms: []
      current_cluster_compared_to_prior: yes | no
    active_exclusion_match: yes | no
    route_changed_by_exclusion: yes | no
    capture_created: yes | no
    exclusion_id: "none | NEG-..."
    handoff_allowed: yes | no
  cybernetic_context:
    required: yes | no
    system_type: clear | complicated | complex | chaotic | mixed | unknown
    pattern: "..."
    feedback_loop: "..."
    leverage_level: parameter | buffer | stock_flow_structure | delay | balancing_loop | reinforcing_loop | information_flow | rules | self_organization | goal | paradigm | none
    selected_intervention:
      route: checklist | expert_analysis | safe_to_fail_probe | stabilize_first | redesign_feedback | change_rules | change_goal | handoff | blocked
      downstream_skill: resolve | fixed-point-driver | review-adjudication | review-compression-compiler | universalist | reduce | negative-ledger | verification-closure | none
    local_patch_allowed: yes | no
    monitoring_or_probe: "..."
  mutation_permit:
    required: yes | no
    emitted: yes | no
    permit_id: "none | RGR-MP-..."
  selected_route:
    route: no-change | validate-only | delete-collapse-canonicalize | normal-form-decision | review-distillation-mode | boundary-redesign | mutate-existing-owner | add-new-surface | blocked
    owner: "..."
    why_this_route: "..."
    why_not_lower_surface: "..."
    why_not_point_fix: "..."
    expansion_warrant: "none | explicit-user | upstream | retired-more-surface | uninhabitable-state"
    proof_matrix:
      - proof_id: "..."
        counterexamples_covered: []
        command_or_test: "..."
    forbidden_actions: []
  proof_matrix_gate:
    required: yes | no
    one_test_per_wound: yes | no
    family_matrix_present: yes | no
    duplicate_fixture_cases: yes | no
    tests_retired_or_merged: []
    allowed: yes | no
  production_embargo:
    required: yes | no
    production_net_allowed: yes | no
    expected_production_net: negative | zero | positive | unknown
    reason: "..."
  actuation_handoff:
    downstream_skill: fixed-point-driver | accretive-implementer | none
    permitted_scope: []
    surface_budget:
      production_surface: zero_or_negative | bounded_positive | explicit_expansion
      helpers_wrappers_adapters_allowed: yes | no
      public_symbols_allowed: yes | no
      fallback_or_compat_paths_allowed: yes | no
    stale_if: []
  outcome_metrics:
    production_insertions: 0
    production_deletions: 0
    production_net: 0
    test_insertions: 0
    test_deletions: 0
    test_net: 0
    helpers_added: 0
    public_symbols_added: 0
    fallback_or_compat_paths_added: 0
    validation_branches_added: 0
    evidence_predicates_added: 0
    duplicate_or_shadow_surfaces_retired: 0
    same_cluster_recurred_after: yes | no | unknown
  gate:
    governor_decision_complete: pass | fail
    same_cluster_stop_rule: pass | fail | not-triggered
    mutation_permit: pass | fail | not-required
    production_embargo: pass | fail | not-required
    owner_coarseness_gate: pass | fail | not-required
    boundary_inventory_gate: pass | fail | not-required
    negative_route_gate: pass | fail | not-required
    cybernetic_gate: pass | fail | not-required
    proof_matrix_gate: pass | fail | not-required
    evidence_discipline_complete: pass | fail
    implementation_handoff_allowed: yes | no
```

Prose may explain the record. Prose is not the record.

If the record cannot show why the selected route reduces review entropy without unbounded surface growth, do not mutate.

## Evidence discipline

Every review-derived finding must separate:

```yaml
evidence_discipline:
  observed_fact: "..."
  review_claim: "..."
  proposed_change: "..."
  uncertainty: "..."
  scope_basis: "..."
```

Use `$review-adjudication` when actionability is contested. Use this field even when `$review-adjudication` is root-equivalent.

## Cybernetic context

Use `$cybernetic` when repeated events imply structure, especially:

- same-cluster stop rule;
- local fix loop;
- review feedback keeps producing adjacent findings;
- local proof passes but CAS finds family-adjacent counterexamples;
- metrics/proxies/incentives/delays are shaping behavior.

If same-cluster governor rule fires, either produce `cybernetic_context` or explicitly state why the cluster is not a system pattern.

If `cybernetic_context.local_patch_allowed: no`, do not route another ordinary local mutation.

## Review distillation mode

Use when the review loop itself should not be delivered.

```text
Review lab learns. Delivery branch forgets.
```

Trigger when:

- same-cluster findings continue after governor decision;
- dirty tree contains multiple review-driven repairs;
- CAS keeps finding adjacent issues after green local proof;
- exploratory repair history exists and should not become branch history;
- proposed route would add public/fallback/compatibility/tolerance surface.

Policy:

1. Freeze delivery base.
2. Use lab branch/worktree for exploration.
3. Lift lab findings and repairs into counterexamples.
4. Select a clean normal form.
5. Rebuild from delivery base.
6. Do not cherry-pick lab commits by default.
7. Distill lab tests into proof matrix.
8. Prove delivery covers counterexample family.

## Implementation handoff

Do not hand off raw review findings.

Handoff must include:

```yaml
implementation_handoff:
  selected_route:
  owner:
  mutation_permit:
  permitted_scope: []
  forbidden_actions: []
  surface_budget:
  proof_matrix: []
  negative_route_gate:
  owner_coarseness_gate:
  boundary_inventory:
  proof_matrix_gate:
  production_embargo:
  cybernetic_context:
  stale_if: []
```

If `$fixed-point-driver` or `$accretive-implementer` is invoked, it must preserve the selected route and not expand into local patching outside the governor decision.

## Validation, commit, push

After three clean reviews, run full validation. If validation fails and mutation may result, route failure through the same governor process.

Only after final review streak and validation:

1. inspect status/diff;
2. stage intended changes only;
3. commit intended changes;
4. push current branch;
5. run PR sweep.

Checkpoint commits are allowed after coherent green slices, but they are not final closure.

## PR sweep

After push, inspect associated PR and complete review-thread/comment inventory.

Every actionable PR item uses the same process:

```text
sense -> estimate state -> govern -> permit -> actuate -> observe -> learn
```

If PR handling changes branch state, reset review streak and repeat review/validation/commit/push/sweep.

## Governor compliance reporting

Every final `$resolve` report must include:

```yaml
governor_compliance:
  finding_bearing_waves:
  review_governor_records_required:
  review_governor_records_emitted:
  same_cluster_stop_events:
  mutation_permits_required:
  mutation_permits_emitted:
  mutations_after_stop_rule:
  mutations_after_stop_rule_without_permit:
  mutations_after_stop_rule_with_positive_production_net:
  positive_production_net_embargo_required:
  positive_production_net_embargo_passed:
  owner_coarseness_gate_required:
  owner_coarseness_gate_passed:
  boundary_inventory_required:
  boundary_inventory_emitted:
  negative_ledger_required:
  negative_ledger_operational:
  proof_matrix_gate_required:
  proof_matrix_gate_passed:
```

This must be reported even when the run blocks.

## Report learning contract

Every final `$resolve` report must support future learning.

Include:

```yaml
resolve_learning_report:
  report_version: RLR-v3
  material_improvement:
    apply_patch_calls:
    commits:
    production_insertions:
    production_deletions:
    production_net:
    test_insertions:
    test_deletions:
    test_net:
    same_cluster_findings:
    same_cluster_findings_after_first_fix:
    helpers_wrappers_adapters_added:
    public_symbols_added:
    fallback_or_compat_paths_added:
    validation_branches_added:
    evidence_predicates_added:
    duplicate_or_shadow_surfaces_retired:
  cluster_trajectory: []
  finding_to_route_matrix: []
  decision_impact: []
  skill_obligation_matrix: []
  governor_compliance:
  recommendation_carry_forward: []
  report_confidence:
  report_value_score:
```

The final report must answer:

```text
Did same-cluster recurrence drop?
Did production net growth drop?
Did owner growth stop after recurrence?
Were all post-recurrence mutations permitted?
Did tests become a matrix instead of a wound catalog?
Did negative evidence change a route?
Did CAS iterations per cluster decrease?
```

## Material improvement score

Every final `$resolve` report must include:

```yaml
resolve_material_improvement:
  review_findings_total:
  same_cluster_findings:
  same_cluster_findings_after_first_fix:
  cas_review_iterations:
  apply_patch_calls:
  commits:
  production_insertions:
  production_deletions:
  production_net:
  test_insertions:
  test_deletions:
  test_net:
  helpers_wrappers_adapters_added:
  public_symbols_added:
  fallback_or_compat_paths_added:
  validation_branches_added:
  evidence_predicates_added:
  duplicate_or_shadow_surfaces_retired:
  selected_routes:
    no_change:
    validate_only:
    delete_collapse_canonicalize:
    normal_form_decision:
    review_distillation_mode:
    boundary_redesign:
    mutate_existing_owner:
    add_new_surface:
    blocked:
  mutation_permits:
    required:
    emitted:
    missing:
    blocked:
  negative_evidence:
    checks:
    operational_checks:
    active_exclusions:
    route_changed_by_exclusion:
  cybernetic:
    contexts_required:
    contexts_emitted:
    route_changed:
  owner_coarseness:
    required:
    owner_too_coarse:
    route_changed:
  proof_matrix:
    gates_required:
    one_test_per_wound_blocked:
    tests_retired_or_merged:
  outcome:
    resolved:
    blocked:
    churn_reduced:
```

No final success claim without this score.

## Final report

End with:

```text
Resolve Bottom Line:
- status: resolved | blocked | partial
- review_backend/base/head:
- clean_review_streak:
- governor_decision:
- selected_route:
- mutation_permit:
- production_embargo:
- owner_coarseness_gate:
- boundary_inventory:
- negative_route_gate:
- proof_matrix_gate:
- cybernetic_context:
- surface_delta_call:
- validation:
- PR sweep:
- governor_compliance:
- material_improvement:
- learning_report_value:
- open blocker:
- exact next action:
```

## Non-negotiables

- CAS-first; native review fallback-only.
- Three clean pinned review runs required.
- Reviews sense; the governor decides; implementation obeys.
- Review findings are counterexamples, not tasks.
- After the second same-cluster finding, local patching is disabled.
- After recurrence, no production mutation without `RGR-V2-MUTATION-PERMIT`.
- After recurrence, positive production net is embargoed unless explicitly warranted.
- Same coarse owner growth requires owner-coarseness adjudication.
- Negative-ledger operational evidence is required before repeated-route mutation.
- Boundary inventory is required when the same owner absorbs recurring semantic branches.
- Proof-matrix gate is required after same-cluster recurrence.
- Do not mutate without a complete `review_governor_record` when the governor rule applies.
- Do not repeat an actively excluded route unless reopened/stale/superseded/accepted.
- Do not route implementation outside the selected route.
- Add-new-surface is expansion and requires explicit warrant.
- Do not claim resolved with failed validation, stale review tuple, open governor gate, missing mutation permit, active negative exclusion, incomplete PR sweep, or missing material-improvement score.
- Do not claim learning improvement without governor-compliance and outcome metrics.

## Resources

- [review-governor-record.md](references/review-governor-record.md)
- [mutation-permit-interlock.md](references/mutation-permit-interlock.md)
- [same-cluster-governor-rule.md](references/same-cluster-governor-rule.md)
- [production-net-embargo.md](references/production-net-embargo.md)
- [owner-coarseness-gate.md](references/owner-coarseness-gate.md)
- [boundary-inventory.md](references/boundary-inventory.md)
- [negative-ledger-operational-evidence.md](references/negative-ledger-operational-evidence.md)
- [proof-matrix-gate.md](references/proof-matrix-gate.md)
- [governor-compliance-reporting.md](references/governor-compliance-reporting.md)
- [review-entropy.md](references/review-entropy.md)
- [finding-to-route-matrix.md](references/finding-to-route-matrix.md)
- [decision-impact-reporting.md](references/decision-impact-reporting.md)
- [cluster-trajectory.md](references/cluster-trajectory.md)
- [material-improvement-score.md](references/material-improvement-score.md)
- [evidence-discipline.md](references/evidence-discipline.md)
- [rgr-gate.md](references/rgr-gate.md)
- [mutation-permit-gate.md](references/mutation-permit-gate.md)
