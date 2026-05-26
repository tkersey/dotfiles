# Adversarial eval seeds

Use these cases to test whether `$review-adjudication` is a true discriminative
filter and a safe downstream selection boundary rather than a rubber-stamp or
"all are worth resolving" prompt.

Track these metrics over time:

- `act_precision`
- `false_act_rate`
- `address_precision`
- `false_address_rate`
- `stale_rejection_rate`
- `wrong_fix_separation_rate`
- `identity_coverage_rate`
- `comment_inventory_coverage_rate`
- `artifact_state_coverage_rate`
- `evidence_ref_coverage_rate`
- `decision_test_coverage_rate`
- `resolve_countercase_coverage_rate`
- `all_action_justification_rate`
- `all_selected_justification_rate`
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

1. valid Compact-Gated v3 output
2. dropped input comment
3. validation-only routed as implementation
4. inconsistent Resolve Selection
5. duplicate singleton section
6. Handoff Agenda smuggling non-address rows into implementation
7. all-selected output without structured All-Selected Justification
8. narrow-local action over-routed to `$fixed-point-driver`

## Seed cases

### 1. Valid concern, valid fix

Reviewer correctly identifies a real regression and proposes the minimum safe
change. Expected: `act`; `address`; no-change status `defeated`; current evidence
ref and proof ref; narrow handoff.

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
goal. Expected: `rebut` or `defer`; relevance `preference-only`; resolve decision
`do-not-address` unless the user explicitly wants it.

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

Failure mode might be real but cannot be established. Expected:
`need-evidence`, `proposed_fix_validity: validation-only`, `validate-only`, route
rationale `validation-only`, `implementation_handoff_allowed: no`, and
`validation_handoff_allowed: yes`.

### 9. All comments valid

Every comment is genuinely grounded and material. Expected: all `act` and likely
all `address`, but only with structured All-Action Justification and structured
All-Selected Justification.

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
