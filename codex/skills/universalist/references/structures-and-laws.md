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

Use when a boundary requires free syntax, coherent observations, transported semantics, lifted implementations, explicit IR, or residual obligations. Laws depend on the artifact: preservation, coherence, projection, lowering, or interpreter equivalence.


## Freyd / premonoidal category

Use when pure values and effectful computations share types but order is observable. Laws: pure embedding preserves identity/composition; central operations commute; effect reordering requires observational commutativity.

## Colored operad

Use when typed components assemble hierarchically and a composite remains a component. Laws: port typing, identity wiring, associative substitution, and semantic interpretation preserving substitution.

## PROP / properad / traced structure

Use when multiple outputs or feedback are fundamental rather than conveniently bundled. Laws: network composition/feedback preserves the chosen semantic observations and resource constraints.
