# Structures and laws

## Product

Use when independent fields must coexist. Laws: projections recover fields; constructor/projection round-trip.

## Coproduct

Use when cases are mutually exclusive. Laws: exhaustive handling; impossible states rejected.

## Refined type / equalizer

Use when repeated predicates should be centralized. Laws: valid accepted, invalid rejected, normalization idempotent.

## Pullback

Use when two values must agree on a shared projection. Laws: mismatch rejected; projections preserved.

## Exponential

Use when behavior should be supplied rather than branched. Laws: strategy/callback parity against old branch fixtures.

## Free construction / initial algebra

Use when syntax should be separated from execution. Laws: interpreters agree on fixtures; fold/interpreter totality.

## Canonical boundary artifact

Use when a boundary requires free syntax, coherent observations, transported semantics, lifted implementations, free builders, explicit IR, or residual obligations. Laws depend on the artifact: preservation, coherence, projection, lowering, or interpreter equivalence.

## Freyd/AFT-style projection diagnostic

Use when a lift-shaped boundary depends on a projection `P : B -> C` from internals to observable behavior. Laws: required behavior embeds into or is satisfied by `P(Free(required))`; missing evidence or missing templates are reported as obstructions.
