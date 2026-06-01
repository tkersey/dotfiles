# Spec Lint Rubric

## Blocking errors

- Missing objective, scope, non-goals, or locked decisions.
- No primary invariant.
- No proof bar or proof commands.
- No requirement-to-test traceability.
- No rollback or abort criteria.
- Material open questions without owner/default/consequence.
- Implementation sequence requires unowned architecture choices.
- `grill_rounds: 0` without a concrete no-grill justification.
- Balanced, strict, or campaign work skipped invariant challenge or fresh-eyes pass.
- Spawned subagents are not accounted for as consumed, rejected, timed out, superseded, or open-at-end zero.
- Output contains `<proposed_plan>` when it is a `spec-pipeline` artifact.

## Material risks

- Long spec with no size-profile justification.
- Public API or migration with weak compatibility posture.
- Runtime behavior represented only by scaffold proof.
- Dependencies not ordered.
- Edge cases are generic rather than project-specific.
- `blocked` appears without `blocked_receipt`.
- Session shape suggests campaign mode but the artifact remains balanced/strict.

## Preferences

- Better naming.
- Tighter prose.
- Extra examples.
- Non-blocking alternative sections.
