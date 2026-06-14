---
name: resolve
description: "Resolve the current branch through a CAS-first, receipt-backed review loop with native review as recorded fallback only. Use for `$resolve`, branch resolution, review/fix/validate/commit/push loops, PR sweep, three consecutive clean reviews, same-cluster stop rule, resolve_decision_record / RDR-v1, negative-ledger route ratchet, review-distillation mode, material-improvement score, and final pushed readiness. Do not use for one-shot review, PR creation only, merging/landing, isolated adjudication, or final closure proof without branch mutation."
---

# resolve

## Purpose

Resolve the current branch to a pinned-review-clean, validated, committed, pushed, and PR-comment-swept state **without unbounded review-driven code accumulation**.

This version is intentionally austere. It keeps the good ideas from the prior iterations, but changes the default from "more packets" to one hard operating rule:

```text
After the second same-cluster finding, stop point-fixing.
```

## Core doctrine

```text
Review findings are counterexamples, not tasks.
Same-cluster recurrence means ordinary resolution mode is over.
Do not deliver the review loop.
Before repeating a route, check negative evidence.
Implement only the selected route.
Measure whether the workflow materially improved.
```

## Activation Kernel

Use `$resolve` when the user wants the current branch driven through review/fix/validate/push/PR-sweep closure.

Do not use `$resolve` when:

- the user wants a one-shot review only;
- the user wants PR creation/proof publication only; use `$ship`;
- the user wants merge/checks-watch/cleanup; use `$land`;
- the user wants actionability only; use `$review-adjudication`;
- the user wants final readiness only; use `$verification-closure`;
- the user wants implementation of a known route only; use `$fixed-point-driver` or `$accretive-implementer`.

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
+ no open same-cluster stop-rule gate
+ no active negative exclusion against the selected route
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

Switching backend/base/head/fingerprint resets the clean-review streak.

## Same-Cluster Stop Rule

A **cluster** is a group of review, validation, or PR findings sharing a subsystem, owner, state machine, protocol, authority boundary, parser/validator, lifecycle, proof surface, or invariant family.

If a second finding appears in the same cluster during one `$resolve` run, `$resolve` must stop review-driven point-fixing.

After the stop rule fires, only these routes are allowed:

1. `validate-only`
2. `delete-collapse-canonicalize`
3. `normal-form-decision`
4. `review-distillation-mode`
5. `blocked`

`mutate-existing-owner` is allowed only when selected by a normal-form decision that names:

- the owner;
- the counterexample family;
- why delete/collapse is insufficient;
- why this is not another local point fix;
- the proof matrix.

`add-new-surface` is disallowed after the stop rule unless the user or an upstream authority explicitly accepts expansion after negative-evidence and universalist/boundary checks.

## Resolve Decision Record

Use one default record instead of multiple mandatory packet types.

A finding-bearing review wave, same-cluster stop, repeated route, distillation decision, or final report must emit or update:

```yaml
resolve_decision_record:
  record_version: RDR-v1
  resolve_run_id: "..."
  artifact_state:
    branch: "..."
    base_sha: "..."
    head_sha: "..."
    target_fingerprint: "..."
  review_wave:
    backend: cas-lane | native-cli | cas-native-fallback | none
    receipt_id: "..."
    finding_ids: []
  cluster:
    cluster_id: "..."
    same_cluster_count: 0
    stop_rule: not-triggered | triggered | closed | blocked
    owner_candidates: []
    counterexample_family: "..."
  selected_route:
    kind: no-change | validate-only | delete-collapse-canonicalize | normal-form-decision | review-distillation-mode | mutate-existing-owner | add-new-surface | blocked
    owner: "..."
    why_this_route: "..."
    why_not_smaller: "..."
    why_not_point_fix: "..."
  negative_evidence:
    checked: yes | no
    active_exclusion_match: yes | no
    exclusion_id: "none | NEG-..."
    status: none | active | reopened | stale | superseded | blocked
    route_changed_by_exclusion: yes | no
  universalist_check:
    required: yes | no
    decision: use-universalist | not-needed | blocked | not-required
    reason: "..."
  distillation:
    required: yes | no
    mode: none | review-lab-to-clean-delivery | blocked
    delivery_base: "..."
    lab_ref: "..."
    scar_tissue_disposition: []
  surface_delta:
    production_insertions: 0
    production_deletions: 0
    production_net: 0
    test_insertions: 0
    test_deletions: 0
    test_net: 0
    helpers_wrappers_adapters_added: 0
    public_symbols_added: 0
    fallback_or_compat_paths_added: 0
    duplicate_or_shadow_surfaces_retired: 0
    surface_delta_call: smaller | same | larger-with-warrant | larger-without-warrant | unknown
  proof_matrix:
    - proof_id: "..."
      counterexamples_covered: []
      command_or_test: "..."
      existing_or_new: existing | new | modified | manual
  implementation_handoff:
    target_skill: fixed-point-driver | accretive-implementer | none
    permitted_scope: []
    forbidden_actions: []
    proof_required: []
  material_improvement:
    same_cluster_findings: 0
    same_cluster_findings_after_first_fix: 0
    cas_review_iterations: 0
    apply_patch_calls: 0
    commits: 0
    route_changed_by_negative_evidence: 0
    compression_or_distillation_changed_route: yes | no
    churn_reduced: yes | no | unknown
  gate:
    stop_rule_satisfied: pass | fail | not-triggered
    negative_route_gate: pass | fail | not-required
    proof_matrix_present: pass | fail
    surface_budget_ok: pass | fail | unknown
    implementation_handoff_allowed: yes | no
```

If the same-cluster stop rule fires, this record is mandatory before any further production mutation.

Prose may explain the record. Prose is not the record.

## Negative-Ledger Route Ratchet

`$negative-ledger` is not another report section. It is a route ratchet.

Before repeating a route in a hot cluster, check whether that route was already falsified.

```yaml
negative_route_gate:
  prior_route_checked: yes | no
  active_exclusion_match: yes | no
  if_match:
    neg_id: "..."
    selected_route: "..."
    exclusion_rule: "..."
    status: reopened | superseded | stale | blocked
  handoff_allowed: yes | no
```

If `active_exclusion_match: yes` and status is not `reopened`, `superseded`, or `stale`, implementation is blocked.

Same-cluster recurrence after a selected route creates a negative-evidence capture candidate unless proven unrelated, stale, or superseded.

## Review Distillation Mode

Review Distillation Mode is the escape hatch for review loops that should not be delivered.

Trigger when any are true:

- same-cluster findings continue after the stop rule;
- dirty tree contains multiple review-driven repairs;
- CAS keeps finding adjacent issues after green local proof;
- exploratory repair history exists and should not become final branch history;
- a proposed route would add public/fallback/compatibility/tolerance surface.

Policy:

```text
The lab learns. The delivery branch forgets.
```

Operationally:

1. Freeze delivery base: branch, head SHA, base SHA, diff digest, proof state.
2. Use a disposable review lab branch/worktree for exploration.
3. Lift lab findings and repairs into counterexamples.
4. Select a clean normal form.
5. Rebuild from delivery base.
6. Do not cherry-pick lab commits by default.
7. Distill lab tests into a proof matrix.
8. Prove delivery branch covers the counterexample family.
9. Discard or retain lab only as evidence.

## Review loop

Repeat until `clean_review_streak == 3`:

1. Run selected review driver.
2. If clean:
   - verify backend/base/head/fingerprint pins;
   - increment streak;
   - run another review if streak < 3.
3. If findings/comments appear:
   - reset streak;
   - invoke `$review-adjudication` for each in-scope item;
   - cluster findings before editing;
   - if same-cluster count is 2, trigger the stop rule;
   - before repeating a route, run negative route ratchet;
   - if stop rule fired, select one allowed route;
   - route implementation through `$fixed-point-driver` / `$accretive-implementer` only after the record permits it;
   - run targeted proof;
   - update material-improvement counters;
   - restart review on current artifact state.

Do not use an arbitrary maximum iteration count. Stop for explicit blockers: unavailable review backend, ambiguous base, required validation unavailable, active negative exclusion, unresolved stop-rule gate, unresolved boundary/owner question, or PR sweep incompleteness.

## Review adjudication route consumption

Do not collapse all review items to `address`.

| adjudication route | `$resolve` handling |
|---|---|
| `address` / `mutate-code` | cluster; stop rule if needed; negative route ratchet; implementation handoff only after selected route |
| `delete-collapse-canonicalize` | prefer after stop rule when behavior can be preserved |
| `validate-only` | proof only; reset streak if files change |
| `resolve-thread-only` | reply/resolve only if provider policy permits |
| `do-not-address` | record rationale; review run still not clean |
| `blocked` | stop before commit/push |

## Final validation

After three clean reviews, run full project validation using repository-native commands from CI, package scripts, task runners, project docs, or language/tool skills.

If validation fails, route it through the same clustering/stop-rule/negative-route process when mutation may result.

If no validation command exists, do not treat validation as passed. Block or explicitly report manual-only proof if accepted by the user.

## Commit and push

Only after final three-review clean streak and full validation:

1. inspect `git status` and diff;
2. stage only intended changes;
3. commit intended changes;
4. push current branch;
5. run PR sweep.

Checkpoint commits are allowed after a coherent green slice, but they are not final closure.

## PR sweep

After push, inspect the associated PR. Prefer complete paginated review-thread inventory. Every in-scope PR item uses the same adjudication → cluster → stop-rule/negative-route → implementation route.

If PR handling changes branch state, reset streak and repeat review/validation/commit/push/sweep.

## Material Improvement Score

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
  compression_or_distillation:
    used:
    changed_route:
  outcome:
    resolved:
    blocked:
    churn_reduced:
```

The success question is not "did we emit packets?" It is:

```text
Did same-cluster recurrence drop?
Did production net growth drop?
Did delete/collapse/refactor routes appear?
Did negative evidence change a route?
Did CAS iterations per cluster decrease?
```

## Final report

End with:

```text
Resolve Bottom Line:
- status: resolved | blocked | partial
- review_backend/base/head:
- clean_review_streak:
- same_cluster_stop_rule:
- selected_route:
- negative_route_gate:
- distillation:
- surface_delta_call:
- validation:
- PR sweep:
- material_improvement:
- open blocker:
- exact next action:
```

## Non-negotiables

- CAS-first; native review fallback-only.
- Three clean pinned review runs required.
- Review findings are counterexamples, not tasks.
- After the second same-cluster finding, stop point-fixing.
- Do not mutate after stop rule until an allowed route is selected.
- Do not repeat an actively excluded route unless reopened/stale/superseded or explicitly accepted.
- Do not deliver review lab history.
- Add-new-surface after stop rule requires explicit expansion acceptance.
- Do not claim resolved without material-improvement score.
- Do not claim resolved with failed validation, stale review tuple, open stop-rule gate, active negative exclusion, or incomplete PR sweep.

## Resources

- [same-cluster-stop-rule.md](references/same-cluster-stop-rule.md)
- [resolve-decision-record.md](references/resolve-decision-record.md)
- [negative-route-ratchet.md](references/negative-route-ratchet.md)
- [review-distillation-mode.md](references/review-distillation-mode.md)
- [material-improvement-score.md](references/material-improvement-score.md)
- [implementation-handoff.md](references/implementation-handoff.md)
- [final-report-contract.md](references/final-report-contract.md)
- [rdr-gate.md](references/rdr-gate.md)
