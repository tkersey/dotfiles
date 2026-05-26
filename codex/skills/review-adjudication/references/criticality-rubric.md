# Criticality rubric

Use this rubric to make `review-adjudication` discriminative rather than
deferential.

## Act threshold

A comment may be marked `act` only when all are true:

1. The concern is grounded in current artifact evidence.
2. The concern is material, or the user explicitly wants the nonmaterial change.
3. The comment is fresh for the current artifact state.
4. The strongest no-change countercase is defeated.
5. The proposed remedy is valid, or the chosen handoff replaces it with a valid
   fix shape.
6. The action does not violate stated PR constraints, non-goals, compatibility
   posture, or ownership boundaries.
7. The row has a current evidence grade:
   - `current-artifact`
   - `current-test`
   - `current-ci`
   - `current-session-artifact`
8. The row has a concrete evidence ref.

If any item fails, choose `rebut`, `defer`, or `need-evidence`.

`act` requires proof, not plausibility.

## Rebut threshold

Use `rebut` when:

- the comment is unsupported by current artifacts
- the comment is stale or superseded
- the comment assumes a contract this PR does not own
- the requested change would make the design less canonical or less sound
- the proposed fix is wrong and the concern itself is not material
- the issue is preference-only and no repo convention supports it
- the no-change countercase remains stronger than the review claim

A rebuttal should include evidence, not attitude.

## Defer threshold

Use `defer` when:

- the concern is real but outside the PR scope
- acting now would broaden the change non-accretively
- the issue belongs to a future migration or separate design decision
- the comment identifies a governing invariant that needs a broader plan before
  this PR should change code
- implementation now would obscure ownership or source-of-truth boundaries

## Need-evidence threshold

Use `need-evidence` when:

- the concern might be real but cannot be established from current artifacts
- a validating check is the correct next move
- `$seq` cannot recover the PR why and the intent matters
- a specialist audit is needed before code should change
- a proposed fix is plausible but the failure mode is not proven

## Validation-only route

Use validation-only when uncertainty is the issue, not implementation effort.
Record:

```md
disposition: need-evidence
reframe_type: validation-only
remediation_posture: validating-check-only
proposed_fix_validity: validation-only
handoff_action: route-to-fixed-point-driver
```

Validation-only may produce tests, repros, probes, or inspections. It must not
apply the reviewer's requested mutation until the validation proves the concern
or current artifacts already prove it.

Checker-level expectations:

- `validation-only` requires `need-evidence`.
- `need-evidence` cannot route directly to `$accretive-implementer`.
- validation handoff is not implementation permission.

## Concern-vs-fix separation

A review comment contains at least two claims:

1. the concern is real
2. the proposed fix is the right fix

Adjudicate them independently.

Examples:

| Concern | Proposed fix | Correct disposition |
|---|---|---|
| valid | valid | `act` with narrow handoff |
| valid | wrong-fix | `act` only if handoff replaces the fix shape |
| valid | overbroad | `act` or `defer`, depending on scope and minimum fix shape |
| unknown | plausible | `need-evidence`, often validation-only |
| unsupported | valid-looking | `rebut` or `need-evidence`; do not mutate from plausibility |
| preference-only | valid-looking | `rebut` unless repo convention or user goal makes it material |

## Local-validity trap

A comment can be locally true and still be the wrong action.

Signs:

- multiple comments are symptoms of one source-of-truth or ownership invariant
- local fixes would create duplicate paths
- the fix would encode a special case rather than repair the governing rule
- the suggested remedy is easier than the correct invariant-level change
- the reviewer is optimizing a local symptom while the PR owns a structural rule

When this happens, mark the comment `partially-relevant` or `material-relevant`,
but route the handoff through an invariant-level agenda instead of isolated local
fixes.

## All-action warning

If every substantive comment is accepted, run an acceptance-skew audit:

- Did we defeat the no-change countercase for every comment?
- Did we identify stale, preference-only, unsupported, or out-of-scope
  possibilities?
- Are several comments really one governing invariant?
- Are we accepting reviewer authority instead of artifact evidence?
- Is at least one accepted action validation-only rather than code change?
- Did we separate concern validity from proposed-fix validity for every comment?
- Does every accepted action have current evidence grade and evidence ref?

If the justification is weak, downgrade appropriate comments to `need-evidence`,
`defer`, or `rebut`. If the justification is missing, block implementation
handoff.


## Resolve-selection rubric

After disposition, select one downstream resolve decision per comment:

- `address`: only for artifact-backed `act` rows whose no-change case is
  defeated.
- `validate-only`: for `need-evidence` rows where proof is the next move, not
  mutation.
- `resolve-thread-only`: for stale, superseded, or already-fixed comments that
  need only a proof-bearing reply or thread resolution.
- `do-not-address`: for preserved no-change cases, rebuttals, deferrals,
  unsupported claims, preference-only items, or out-of-scope asks.
- `blocked`: for missing identity, stale artifact state, absent rationale, or
  insufficient evidence that prevents safe downstream selection.

Never route `resolve-thread-only`, `do-not-address`, or `blocked` items into
implementation.

## Resolve-selection anti-laundering rubric

A comment being valid is not enough to make it worth resolving now. After the
ordinary adjudication disposition, select a downstream resolve decision:

- `address` only when the row is `act`, the no-change case is defeated, current
  evidence exists, and implementation is the correct next move.
- `validate-only` when uncertainty is material and proof should precede mutation.
- `resolve-thread-only` when latest HEAD already satisfies or supersedes the
  comment and a proof-bearing reply/thread resolution is enough.
- `do-not-address` when the preserved no-change case, scope boundary, or low
  value makes downstream work inappropriate.
- `blocked` when identity, artifact state, evidence, or rationale is incomplete.

Run a resolve countercase for every row. If every substantive comment is selected
as `address` or `validate-only`, emit a structured All-Selected Justification.
Do not let `$fixed-point-driver` become the default route for narrow-local work.
