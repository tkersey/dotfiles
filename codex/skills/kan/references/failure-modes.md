# Failure modes

## Modeling failures

- `C` is only a list of nouns, not a category with morphisms.
- `K` maps object names but not morphisms.
- `F` is not functorial; transformations do not preserve composition or identity.
- `E` lacks the limits/colimits the design assumes.
- The unit/counit is not implemented anywhere.
- The claimed law is not testable even approximately.

## `Lan` failures

- Generated/default behavior is too permissive.
- Quotienting merges cases that must remain distinct.
- Generated artifacts bypass the unit compatibility adapter.
- Source behavior is preserved for examples but not for morphisms/transformations.
- The initial/free claim is used to justify an API that actually has multiple uncoordinated construction paths.

## `Ran` failures

- The product of observations is too large or impossible to compute.
- Coherence conditions reject valid business cases because the old observation set is incomplete.
- The facade becomes opaque and unmaintainable.
- Projections are implemented independently and drift.
- A partial observer is treated as total.

## Codensity failures

- Performance is assumed rather than measured.
- Error ordering, laziness/strictness, resource finalization, or logging order changes.
- Rank-n representation leaks through public API unnecessarily.
- The optimization hides the real bottleneck.

## Architecture failures

- The team gets category terms but no simpler code.
- The abstraction has no owner or tests.
- A plain interface would have solved the problem.
- Categorical vocabulary blocks onboarding.
- The code encodes a theorem-shaped fantasy rather than the repository’s actual seams.
