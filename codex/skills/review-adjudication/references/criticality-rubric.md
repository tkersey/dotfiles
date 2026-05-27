# Criticality rubric

Use this rubric to make `review-adjudication` discriminative rather than
deferential, especially for P2+ findings.

## Core rule

A review comment is not implementation work until three independent questions
all pass:

1. **Concern proof**: current artifacts prove the concern.
2. **Direction proof**: the action is aligned with the active PR/codebase
   direction or is direction-overriding because current artifacts prove a
   critical defect.
3. **Mutation value**: the code change is materially valuable to the codebase,
   not merely useful for review closure.

Reviewer severity labels are adjudicated as claims, not inherited as priority.

## Act threshold

A comment may be marked `act` only when all are true:

1. The concern is grounded in current artifact evidence.
2. The concern is fresh for the current artifact state.
3. The action has `direction_fit: aligned` or `direction-overriding`.
4. The row has a concrete `direction_ref`.
5. The action has `mutation_value: codebase-material`.
6. The concern is material to codebase direction, not merely review closure.
7. The strongest no-change countercase is defeated.
8. The proposed remedy is valid, or the chosen handoff replaces it with a valid
   minimum fix shape.
9. The action does not violate stated PR constraints, non-goals, compatibility
   posture, ownership boundaries, or active plan direction.
10. The row has a current evidence grade:
    - `current-artifact`
    - `current-test`
    - `current-ci`
    - `current-session-artifact`
11. The row has a concrete evidence ref.
12. The row has implementation-grade `accepted_criticality`:
    - `blocker`
    - `security-critical`
    - `safety-critical`
    - `data-loss-critical`
    - `correctness-critical`
    - `compatibility-critical`
    - `direction-critical`
13. For P0/P1/P2 reviewer claims, `severity_acceptance_status: accepted` and a
    concrete `severity_proof_ref` are required.

If any item fails, choose `rebut`, `defer`, `need-evidence`, or `blocked`.

`act` requires proof, direction alignment, and material codebase value — not
plausibility, reviewer pressure, or severity labeling.

## P2+ severity threshold

Use this for comments labeled or implied as P0, P1, or P2.

| Reviewer claim state | Required response |
|---|---|
| current artifact proves implementation-grade defect and direction fits | accept severity; `act`/`address` may be legal |
| defect plausible but unproven and validation would change route | `need-evidence`; `validate-only`; no implementation |
| defect real but outside current PR/plan/non-goal | `defer`; `do-not-address` |
| severity label is unsupported or overstated | `rebut` or `defer`; severity `rejected` or `downgraded` |
| issue is review-closure-only | severity `downgraded`; `resolve-thread-only` or `do-not-address` |
| direction conflicts and no direction-overriding defect exists | `defer` or `rebut`; no implementation |

`review-closure-only`, `low-value`, `out-of-lane`, and `unknown` are not
implementation-grade criticalities.

## Direction fit threshold

Use `direction_fit: aligned` when the action is supported by a current,
same-objective direction source:

- explicit current user instruction
- current PR body/issue/design doc
- current same-objective `.step/proposed-plan.md`
- current same-objective `$st` active frontier
- built-in task/update-plan projection that matches `$st` or current objective
- current artifact convention or ownership boundary
- `$seq` recovered same-objective plan/session evidence

Use `direction_fit: direction-overriding` when current artifacts prove a defect
that must be fixed regardless of whether the active plan named it: correctness,
security, safety, data loss, compatibility breakage, or another critical
invariant violation.

Use `direction_fit: neutral` when the comment is not in conflict but does not
materially advance the active direction.

Use `direction_fit: conflicting` when the comment conflicts with current
non-goals, ownership boundaries, compatibility posture, active migration plan,
or codebase direction.

Use `direction_fit: unknown` when available context cannot decide.

## Rebut threshold

Use `rebut` when:

- the comment is unsupported by current artifacts
- the severity label is unsupported, overstated, or review-closure-only
- the comment is stale or superseded
- the comment assumes a contract this PR does not own
- the requested change would make the design less canonical or less sound
- the proposed fix is wrong and the concern itself is not material
- the issue is preference-only and no repo convention supports it
- the action conflicts with current direction and no direction-overriding defect
  exists
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
- the comment is direction-conflicting but valid for a different objective

## Need-evidence threshold

Use `need-evidence` when:

- the concern might be real but cannot be established from current artifacts
- a validating check is the correct next move and would change route selection
- `$seq`/`$st`/plan context cannot recover direction and direction matters
- a specialist audit is needed before code should change
- a proposed fix is plausible but the failure mode is not proven
- a P2+ label might be valid but lacks severity proof

## Validation-only route

Use validation-only when uncertainty is the issue, not implementation effort.
Record:

```md
disposition: need-evidence
reframe_type: validation-only
remediation_posture: validating-check-only
proposed_fix_validity: validation-only
mutation_value: validation-material
handoff_action: route-to-fixed-point-driver
```

Validation-only may produce tests, repros, probes, or inspections. It must not
apply the reviewer's requested mutation until validation proves the concern or
current artifacts already prove it.

Validation-only is invalid when validation would only satisfy curiosity,
reviewer comfort, or review closure.

Checker-level expectations:

- `validation-only` requires `need-evidence`.
- `need-evidence` cannot route directly to `$accretive-implementer`.
- validation handoff is not implementation permission.
- `validate-only` requires `mutation_value: validation-material`.

## Concern-vs-fix-vs-severity separation

A review comment contains at least three claims:

1. the concern is real
2. the proposed fix is the right fix
3. the severity label reflects accepted codebase criticality

Adjudicate them independently.

| Concern | Proposed fix | Severity claim | Correct disposition |
|---|---|---|---|
| valid | valid | accepted P2+ | `act` only if direction and mutation value pass |
| valid | wrong-fix | accepted P2+ | `act` only through replacement/invariant handoff |
| unknown | plausible | P2 unresolved | `need-evidence`, often validation-only |
| unsupported | valid-looking | P2 rejected | `rebut` or `need-evidence`; no mutation |
| preference-only | valid-looking | P2 downgraded | `rebut` unless user goal makes it material |
| valid | valid | review-closure-only | `resolve-thread-only` or `do-not-address` |
| valid | valid | direction-conflicting | `defer` unless direction-overriding defect |

## Local-validity trap

A comment can be locally true and still be the wrong action.

Signs:

- multiple comments are symptoms of one source-of-truth or ownership invariant
- local fixes would create duplicate paths
- the fix would encode a special case rather than repair the governing rule
- the suggested remedy is easier than the correct invariant-level change
- the reviewer is optimizing a local symptom while the PR owns a structural rule
- the comment fits a stale plan but conflicts with the active `$st` frontier

When this happens, mark the comment `partially-relevant` or `material-relevant`,
but route the handoff through an invariant-level agenda instead of isolated local
fixes.

## All-action warning

If every substantive comment is accepted, run an acceptance-skew audit:

- Did we defeat the no-change countercase for every comment?
- Did we identify stale, preference-only, unsupported, out-of-scope,
  direction-conflicting, and review-closure-only possibilities?
- Are several comments really one governing invariant?
- Are we accepting reviewer authority or severity labels instead of artifact
  evidence?
- Is at least one accepted action validation-only rather than code change?
- Did we separate concern validity, proposed-fix validity, and severity
  acceptance for every comment?
- Does every accepted action have current evidence grade/ref and direction ref?

If the justification is weak, downgrade appropriate comments to `need-evidence`,
`defer`, or `rebut`. If the justification is missing, block implementation
handoff.

## Resolve-selection anti-laundering rubric

A comment being valid is not enough to make it worth resolving now. After the
ordinary adjudication disposition, select a downstream resolve decision:

- `address` only when the row is `act`, the no-change case is defeated, current
  evidence exists, direction fit passes, accepted criticality is
  implementation-grade, and implementation is the correct next move.
- `validate-only` when uncertainty is material and proof should precede mutation.
- `resolve-thread-only` when latest HEAD already satisfies or supersedes the
  comment and a proof-bearing reply/thread resolution is enough.
- `do-not-address` when the preserved no-change case, direction conflict, scope
  boundary, review-closure-only value, or low value makes downstream work
  inappropriate.
- `blocked` when identity, artifact state, direction state, severity evidence,
  rationale, or evidence is incomplete.

Run a resolve countercase for every row. If every substantive comment is selected
as `address` or `validate-only`, emit a structured All-Selected Justification.
Do not let `$fixed-point-driver` become the default route for narrow-local work.
