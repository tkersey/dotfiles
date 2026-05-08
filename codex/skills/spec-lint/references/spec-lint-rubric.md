# Spec Lint Rubric

## Blocking errors

- Missing objective, scope, non-goals, or locked decisions.
- No primary invariant.
- No proof bar or proof commands.
- No requirement-to-test traceability.
- No rollback or abort criteria.
- Material open questions without owner/default/consequence.
- Implementation sequence requires unowned architecture choices.

## Material risks

- Long spec with no size-profile justification.
- Public API or migration with weak compatibility posture.
- Runtime behavior represented only by scaffold proof.
- Dependencies not ordered.
- Edge cases are generic rather than project-specific.

## Preferences

- Better naming.
- Tighter prose.
- Extra examples.
- Non-blocking alternative sections.
