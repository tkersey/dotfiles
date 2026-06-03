# Criticality rubric

Use this rubric to make `review-adjudication` discriminative rather than deferential.

## Act threshold

A comment may be marked `act` only when all are true:

1. The concern is grounded in current artifact evidence.
2. The concern is material, or the user explicitly wants the nonmaterial change.
3. The comment is fresh for the current artifact state.
4. The strongest no-change countercase is defeated.
5. The proposed remedy is valid, or the chosen handoff replaces it with a valid fix shape.
6. The action does not violate stated PR constraints, non-goals, compatibility posture, or ownership boundaries.
7. The row has a current evidence grade.
8. The row has a concrete evidence ref.
9. The selected downstream action has adversarial clearance when required.

If any item fails, choose `rebut`, `defer`, or `need-evidence`. `act` requires proof, not plausibility.

## Rebut threshold

Use `rebut` when the comment is unsupported, stale, outside this PR's contract,
preference-only, wrong-fix-only, or weaker than the preserved no-change case.

## Defer threshold

Use `defer` when the concern is real but outside PR scope, belongs to a later
migration/design decision, or would obscure the correct owner boundary if acted
on now.

## Need-evidence threshold

Use `need-evidence` when the concern might be real but cannot be established from
current artifacts, a validating check is the correct next move, or a specialist
audit is needed before code should change.

## Concern-vs-fix separation

Adjudicate concern validity independently from proposed-fix validity. A valid
concern with a wrong or overbroad proposed fix may require a replacement fix
shape, invariant-level route, validation-only route, or deferral.

## Local-validity trap

A comment can be locally true and still be the wrong action when multiple
comments are symptoms of one source-of-truth or ownership invariant. Route the
invariant, not isolated local patches.

## Resolve-selection anti-laundering rubric

A valid concern is not automatically worth resolving now. Use `address` only for
artifact-backed `act`; `validate-only` for proof-first uncertainty;
`resolve-thread-only` for already-fixed/stale proof cleanup; `do-not-address` for
preserved no-change/scope/low-value rows; and `blocked` for missing identity,
artifact state, evidence, or rationale.

## Warrant threshold

A downstream action is allowed only when a Resolution Warrant exists for the raw
claim and grants the exact action.

## Least-surface action threshold

A valid `act` decision does not automatically justify additive code. Before
mutation permission, decide the least-surface solution shape and surface budget.
