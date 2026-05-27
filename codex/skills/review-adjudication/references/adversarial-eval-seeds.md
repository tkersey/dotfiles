# Adversarial eval seeds

Use these cases to test whether `$review-adjudication` is a true discriminative
filter and a safe downstream selection boundary rather than a rubber-stamp,
severity-label laundering, or "all are worth resolving" prompt.

Track these metrics over time:

- `act_precision`
- `false_act_rate`
- `address_precision`
- `false_address_rate`
- `stale_rejection_rate`
- `wrong_fix_separation_rate`
- `direction_fit_coverage_rate`
- `direction_conflict_rejection_rate`
- `same_objective_direction_rate`
- `p2_plus_acceptance_precision`
- `p2_plus_false_accept_rate`
- `p2_plus_downgrade_rate`
- `review_closure_mutation_rejection_rate`
- `validation_value_precision`
- `identity_coverage_rate`
- `comment_inventory_coverage_rate`
- `artifact_state_coverage_rate`
- `evidence_ref_coverage_rate`
- `decision_test_coverage_rate`
- `resolve_countercase_coverage_rate`
- `all_action_justification_rate`
- `all_selected_justification_rate`
- `all_p2_plus_accepted_justification_rate`
- `invariant_clustering_rate`
- `validation_only_routing_rate`
- `resolve_selection_coverage_rate`
- `handoff_agenda_consistency_rate`
- `handoff_agenda_leak_rate`
- `duplicate_section_rejection_rate`
- `resolve_proof_ref_coverage_rate`
- `fixed_point_overrouting_rate`
- `selection_countercase_coverage_rate`
- `gate_failure_when_incomplete_rate`

## Checker fixture classes

Maintain fixtures for:

1. valid Compact-Gated v4 output
2. dropped input comment
3. validation-only routed as implementation
4. inconsistent Resolve Selection
5. duplicate singleton section
6. Handoff Agenda smuggling non-address rows into implementation
7. all-selected output without structured All-Selected Justification
8. narrow-local action over-routed to `$fixed-point-driver`
9. P2+ label accepted without severity proof
10. P2+ review-closure-only mutation
11. direction-conflicting action selected as address
12. validation-only selected without material validation value
13. `$st`/plan direction used while stale or off-target

## Seed cases

### 1. Valid concern, valid fix

Reviewer correctly identifies a real regression and proposes the minimum safe
change. Expected: `act`; `address`; no-change status `defeated`; direction fit
`aligned` or `direction-overriding`; accepted criticality implementation-grade;
current evidence ref and proof ref; narrow handoff.

### 2. Valid concern, wrong fix

Reviewer identifies a real bug but proposes a local special case that violates
the source-of-truth rule. Expected: concern `valid`; proposed fix `wrong-fix` or
`overbroad`; `act` only through replacement/invariant-level handoff; resolve
countercase required.

### 3. Stale comment after later patch

Reviewer comment was true on an earlier diff but is superseded by the current
artifact state. Expected: `rebut` or `defer`; relevance `stale-or-superseded`;
`resolve-thread-only` or `do-not-address`; no implementation handoff.

### 4. Preference-only comment without convention

Reviewer requests a naming/style change unsupported by repo convention or user
goal. Expected: `rebut` or `defer`; relevance `preference-only`; resolve
decision `do-not-address` unless the user explicitly wants it.

### 5. Out-of-scope broadening request

Reviewer asks the PR to solve an adjacent migration or unrelated design problem.
Expected: `defer`; relevance `out-of-scope`; resolve decision `do-not-address`;
no code mutation in this PR.

### 6. Unsupported reviewer intuition

Reviewer says a path "seems unsafe" but current artifacts, tests, and contracts
do not ground the failure. Expected: `need-evidence` or `rebut`; never direct
`act` or `address` without current evidence.

### 7. Locally valid but invariant-level issue

Multiple comments point to the same ownership or source-of-truth invariant.
Expected: cluster into Governing Invariant Ledger; avoid piecemeal local fixes;
route rationale `coupled-comments`, `invariant-level`, or `structural`.

### 8. Validation-only uncertainty

Failure mode might be real but cannot be established, and validation would change
route selection. Expected: `need-evidence`, `proposed_fix_validity:
validation-only`, `mutation_value: validation-material`, `validate-only`, route
rationale `validation-only`, `implementation_handoff_allowed: no`, and
`validation_handoff_allowed: yes`.

### 9. All comments valid

Every comment is genuinely grounded, material, direction-aligned, and
implementation-critical. Expected: all `act` and likely all `address`, but only
with structured All-Action Justification and structured All-Selected
Justification.

### 10. All comments plausible, only some grounded

Reviewer provides plausible but mixed-quality comments. Expected: some `act`,
some `need-evidence`/`rebut`/`defer`; some `address`, some
`validate-only`/`resolve-thread-only`/`do-not-address`; gate blocks if output
collapses all to selected work without proof.

### 11. All-worth-resolving laundering

The user asks to refine comments to those worth resolving. The model says all are
worth resolving despite mixed evidence. Expected: failure unless structured
All-Selected Justification proves every item deserves `address` or
`validate-only`.

### 12. Handoff Agenda smuggling

Resolve Selection is correct, but Handoff Agenda routes all IDs to
implementation. Expected: checker failure on `handoff_agenda_consistency`.

### 13. Duplicate section contradiction

Output contains two `Resolve Selection` sections with conflicting rows. Expected:
checker failure by duplicate singleton-section rejection.

### 14. Fixed-point over-routing

A single narrow local action is routed to `$fixed-point-driver` without coupled,
invariant, structural, contentious, validation-only, or reopening rationale.
Expected: checker failure or hard warning; use `$accretive-implementer` for
`narrow-local` implementation.

### 15. Proof-only thread cleanup

Comment is already fixed on latest HEAD and needs only a proof-bearing reply.
Expected: `resolve-thread-only`, route rationale `proof-only-thread`, concrete
proof ref, `implementation_handoff_allowed: no`, `reply_handoff_allowed: yes`.

### 16. P2 label without artifact proof

Reviewer labels a plausible issue P2, but current artifacts do not prove
reachability or impact. Expected: severity `rejected` or `unresolved`;
`need-evidence` or `rebut`; no `address`; no implementation handoff.

### 17. P2 review-closure-only

Reviewer labels a review-closure preference as P2. Expected: severity
`downgraded`; accepted criticality `review-closure-only`; `resolve-thread-only`
or `do-not-address`; no implementation handoff.

### 18. P2 valid but direction-conflicting

Reviewer identifies a real concern, but the requested action conflicts with
active non-goals or locked plan direction. Expected: `direction_fit:
conflicting`; `defer` or `rebut`; `do-not-address`; no implementation handoff.

### 19. P2 validation curiosity

Reviewer raises a plausible P2, but validation would not change merge, release,
invariant, accepted criticality, or implementation direction. Expected: no
`validate-only`; no implementation handoff.

### 20. P2 aligned current defect

Reviewer labels P2 and current artifacts prove a direction-aligned correctness
defect. Expected: severity `accepted`; accepted criticality
`correctness-critical`, `compatibility-critical`, or `direction-critical`;
direction fit `aligned` or `direction-overriding`; `act`; `address`.

### 21. Stale `$st` direction laundering

An old `$st` frontier points at broad hardening, but the current PR is a narrow
bug fix and the plan is stale/off-target. Expected: direction source cannot
justify `act`; affected rows become `defer`, `rebut`, `need-evidence`, or
`blocked`.

### 22. Built-in plan projection overused

The built-in task list says "fix reviews", but `$st` and the PR body indicate a
narrow goal. Expected: update-plan projection is not enough for scope expansion;
`direction_ref` must come from current same-objective direction or current
artifacts.
