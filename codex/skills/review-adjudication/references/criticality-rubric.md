# Criticality rubric

Use this rubric to make `review-adjudication` discriminative rather than deferential.

## Act threshold
A comment may be marked `act` only when:
1. it is grounded in current artifact evidence,
2. the concern is material or the user explicitly wants the nonmaterial change,
3. the no-change countercase is defeated,
4. the proposed remedy or handoff shape is valid,
5. the action does not violate stated PR constraints.

If any of these fail, choose `rebut`, `defer`, or `need-evidence`.

## Rebut threshold
Use `rebut` when:
- the comment is unsupported by artifacts,
- the comment is stale or superseded,
- the comment assumes a contract this PR does not own,
- the requested change would make the design less canonical or less sound,
- the proposed fix is wrong and the concern itself is not material,
- the issue is preference-only and no repo convention supports it.

A rebuttal should include evidence, not attitude.

## Defer threshold
Use `defer` when:
- the concern is real but outside the PR scope,
- acting now would broaden the change non-accretively,
- the issue belongs to a future migration or separate design decision,
- the comment identifies a governing invariant that needs a broader plan.

## Need-evidence threshold
Use `need-evidence` when:
- the concern might be real but cannot be established from current artifacts,
- a validating check is the correct next move,
- `$seq` cannot recover the PR why and the intent matters,
- a specialist audit is needed before code should change.

## Local-validity trap
A comment can be locally true and still be the wrong action.

Signs:
- multiple comments are symptoms of one source-of-truth or ownership invariant,
- local fixes would create duplicate paths,
- the fix would encode a special case rather than repair the governing rule,
- the suggested remedy is easier than the correct invariant-level change.

When this happens, mark the comment `partially-relevant` or `material-relevant`, but route the handoff through an invariant-level agenda instead of isolated local fixes.

## All-action warning
If every substantive comment is accepted, run an acceptance-skew audit:
- Did we defeat the no-change countercase for every comment?
- Did we identify stale, preference-only, unsupported, or out-of-scope possibilities?
- Are several comments really one governing invariant?
- Are we accepting reviewer authority instead of artifact evidence?
- Is at least one accepted action validation-only rather than code change?

If the answer is weak, downgrade appropriate comments to `need-evidence`, `defer`, or `rebut`.
