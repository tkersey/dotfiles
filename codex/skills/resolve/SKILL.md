---
name: resolve
description: "Resolve the current branch through a CAS-first Review Governor: reviews sense, the governor decides, implementation obeys. Use for `$resolve`, branch resolution, review/fix/validate/commit/push loops, PR sweep, three consecutive clean reviews, review_governor_record / RGR-v1, review-entropy reduction, same-cluster recurrence, negative-ledger route memory, cybernetic context, finding-to-route matrices, decision-impact reports, and material-improvement scoring. Do not use for one-shot review, PR creation only, merging/landing, isolated adjudication, or final closure proof without branch mutation."
---

# resolve

## Purpose

Resolve the current branch to a pinned-review-clean, validated, committed, pushed, and PR-comment-swept state without letting review feedback directly actuate code.

`$resolve` is now a **Review Governor**.

```text
Reviews sense. The governor decides. Implementation obeys.
```

Review findings, CAS findings, PR comments, and validation failures are sensor signals. They are not tasks. `$resolve` converts them into counterexample families, estimates review entropy, chooses the lowest-surface entropy-reducing intervention, then permits implementation only through that selected route.

## Core doctrine

```text
Do not satisfy the reviewer. Govern the feedback loop.
Review findings are counterexamples, not tasks.
After the second same-cluster finding, local patching is disabled.
Negative-ledger is route memory, not a decorative preflight note.
Cybernetic classifies repeated feedback patterns, not isolated bugs.
No decision-impact record, no claim of learning.
No material-improvement score, no claim of improvement.
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
+ review_governor_record emitted for finding-bearing waves
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
   - Cluster findings.
   - Track same-cluster count and findings after first fix.
   - Estimate review entropy.
   - Classify system context when repeated events imply structure.

3. **Govern**
   - Enumerate candidate routes.
   - Check negative route memory before repeating a route.
   - Select the route that reduces review entropy with the least system surface.
   - Disable local patching after same-cluster recurrence unless the route is a named normal form.

4. **Actuate**
   - Hand off only the selected route to `$fixed-point-driver` / `$accretive-implementer`.
   - Preserve forbidden actions, proof matrix, and surface budget.

5. **Observe**
   - Run targeted proof.
   - Update surface delta and cluster trajectory.
   - Commit coherent green slices only when safe.
   - Restart review on the current tuple.

6. **Learn**
   - Capture route failures as negative evidence.
   - Update decision-impact and material-improvement metrics.
   - Carry recommendation outcomes into the final report.

## Review entropy

Review entropy is the system’s tendency to keep generating unresolved or adjacent review findings.

Track:

```yaml
review_entropy:
  unresolved_counterexample_families:
  same_cluster_recurrence:
  production_surface_growth:
  helper_wrapper_adapter_growth:
  public_surface_growth:
  fallback_or_compatibility_growth:
  proof_matrix_sprawl:
  repeated_failed_route_penalty:
  delayed_feedback_risk:
```

A patch is allowed only when the selected route reduces review entropy better than the available alternatives.

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
6. `blocked`

`mutate-existing-owner` is allowed only as the implementation form of `normal-form-decision`, and only if the record names:

- the owner;
- the counterexample family;
- why delete/collapse is insufficient;
- why this is not another local point fix;
- the proof matrix.

`add-new-surface` is not a normal route. It is a capital expenditure. It requires explicit expansion warrant, paid abstraction rent, and proof that lower-surface routes cannot satisfy the counterexample family.

## Review Governor Record

Every finding-bearing review wave and every same-cluster governor decision must emit or update:

```yaml
review_governor_record:
  record_version: RGR-v1
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
      proof_matrix_sprawl: 0
      repeated_failed_route_penalty: 0
  candidate_routes:
    - route: no-change | validate-only | delete-collapse-canonicalize | normal-form-decision | review-distillation-mode | blocked
      counterexamples_covered: []
      production_surface_delta: negative | zero | bounded-positive | expansion | unknown
      proof_cost: low | medium | high | unknown
      recurrence_risk: low | medium | high | unknown
      rejected_because: "..."
  negative_memory:
    checked: yes | no
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
  selected_route:
    route: no-change | validate-only | delete-collapse-canonicalize | normal-form-decision | review-distillation-mode | mutate-existing-owner | add-new-surface | blocked
    owner: "..."
    why_this_route: "..."
    why_not_lower_surface: "..."
    why_not_point_fix: "..."
    proof_matrix:
      - proof_id: "..."
        counterexamples_covered: []
        command_or_test: "..."
    forbidden_actions: []
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
    duplicate_or_shadow_surfaces_retired: 0
    same_cluster_recurred_after: yes | no | unknown
  gate:
    governor_decision_complete: pass | fail
    negative_route_gate: pass | fail | not-required
    cybernetic_gate: pass | fail | not-required
    evidence_discipline_complete: pass | fail
    proof_matrix_present: pass | fail
    implementation_handoff_allowed: yes | no
```

Prose may explain the record. Prose is not the record.

If the record cannot show why the selected route reduces review entropy, do not mutate.

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

## Negative route memory

Before repeating any route in a hot cluster:

```yaml
negative_route_gate:
  checked: yes | no
  active_exclusion_match: yes | no
  route_changed_by_exclusion: yes | no
  capture_created: yes | no
  handoff_allowed: yes | no
```

If active negative evidence excludes the route and is not reopened, stale, superseded, or explicitly accepted, implementation is blocked.

Same-cluster recurrence after a selected route creates a negative-evidence capture candidate unless proven unrelated.

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
  permitted_scope: []
  forbidden_actions: []
  surface_budget:
  proof_matrix: []
  negative_route_gate:
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
sense -> estimate state -> govern -> actuate -> observe -> learn
```

If PR handling changes branch state, reset review streak and repeat review/validation/commit/push/sweep.

## Report learning contract

Every final `$resolve` report must support future learning.

Include:

```yaml
resolve_learning_report:
  report_version: RLR-v1
  denominator:
    raw_sessions:
    false_positives:
    effective_sessions:
    confidence:
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
    duplicate_or_shadow_surfaces_retired:
  cluster_trajectory: []
  finding_to_route_matrix: []
  decision_impact: []
  skill_obligation_matrix: []
  recommendation_carry_forward: []
  report_confidence:
    denominator_quality:
    false_positive_count:
    attribution_gaps: []
    confidence:
  report_value_score:
    answered_material_question:
    identified_route_changing_gap:
    measured_outcome_delta:
    separated_invocation_from_impact:
    produced_testable_next_change:
    avoided_skill_mention_theatre:
    overall:
```

The final report must answer:

```text
Did same-cluster recurrence drop?
Did production net growth drop?
Did delete/collapse/refactor routes appear?
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
  duplicate_or_shadow_surfaces_retired:
  selected_routes:
    no_change:
    validate_only:
    delete_collapse_canonicalize:
    normal_form_decision:
    review_distillation_mode:
    mutate_existing_owner:
    add_new_surface:
    blocked:
  negative_evidence:
    checks:
    active_exclusions:
    route_changed_by_exclusion:
  cybernetic:
    contexts_required:
    contexts_emitted:
    route_changed:
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
- negative_route_gate:
- cybernetic_context:
- surface_delta_call:
- validation:
- PR sweep:
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
- Do not mutate without a complete review_governor_record when the governor rule applies.
- Do not repeat an actively excluded route unless reopened/stale/superseded/accepted.
- Do not route implementation outside the selected route.
- Add-new-surface is expansion and requires explicit warrant.
- Do not claim resolved with failed validation, stale review tuple, open governor gate, active negative exclusion, incomplete PR sweep, or missing material-improvement score.
- Do not claim learning improvement without decision-impact and outcome metrics.

## Resources

- [review-governor-record.md](references/review-governor-record.md)
- [same-cluster-governor-rule.md](references/same-cluster-governor-rule.md)
- [review-entropy.md](references/review-entropy.md)
- [finding-to-route-matrix.md](references/finding-to-route-matrix.md)
- [decision-impact-reporting.md](references/decision-impact-reporting.md)
- [cluster-trajectory.md](references/cluster-trajectory.md)
- [skill-obligation-matrix.md](references/skill-obligation-matrix.md)
- [recommendation-carry-forward.md](references/recommendation-carry-forward.md)
- [material-improvement-score.md](references/material-improvement-score.md)
- [negative-route-gate.md](references/negative-route-gate.md)
- [cybernetic-governor-context.md](references/cybernetic-governor-context.md)
- [evidence-discipline.md](references/evidence-discipline.md)
- [companion-receipts.md](references/companion-receipts.md)
- [cas-worker-attribution-spec.md](references/cas-worker-attribution-spec.md)
- [rgr-gate.md](references/rgr-gate.md)
