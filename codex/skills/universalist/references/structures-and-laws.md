# Structures and laws

## Product

Use when independent fields must coexist. Laws: projections recover fields; constructor/projection round-trip.

## Coproduct

Use when cases are mutually exclusive. Laws: exhaustive handling; impossible states rejected.

## Refined type / equalizer

Use when repeated predicates should be centralized. Laws: valid accepted, invalid rejected, normalization idempotent.

## Pullback

Use when two values, models, contexts, or interfaces must agree through maps to a shared target.

```text
f : A -> C
g : B -> C
P = A x_C B
```

Practical laws:

- `f(projectA(p)) == g(projectB(p))`;
- mismatches are rejected at construction;
- both projections are preserved;
- every compatible alternate pair factors through the canonical witness object;
- uniqueness is approximated by one opaque constructor/normal form and no unchecked bypass.

Typical software forms: equijoins, authorization contexts, wire/domain compatibility witnesses, synchronized configuration/state, and evidence joined to required claims.

## Pushout

Use when two source worlds must be glued along an explicit overlap.

```text
i : O -> A
j : O -> B
Q = A +_O B
```

Practical laws:

- `injectA(i(o)) == injectB(j(o))`;
- only declared overlap is identified;
- non-overlap structure and provenance survive;
- conflict is surfaced or resolved by named policy;
- every compatible pair of downstream consumers factors through the integrated artifact;
- uniqueness is approximated by canonical IDs/quotients and one public integration path.

Typical software forms: schema/data integration, modular API or language extension, canonical models, and overlap-based context reconciliation.

## Pushout complement / double-pushout rewrite

Use for graph/model transformations with delete-preserve-add structure:

```text
L <- K -> R
```

The pushout complement removes `L-K` from a matched host while preserving `K`; a second pushout adds `R-K`. Laws: preserved interface unchanged, deletions/additions exact, dangling and forbidden-identification cases rejected, failed complement reported as obstruction. Prefer adhesive or adhesive-like categories when local rewrites must compose predictably.

## Exponential

Use when behavior should be supplied rather than branched. Laws: strategy/callback parity against old branch fixtures.

## Free construction / initial algebra

Use when syntax should be separated from execution. Laws: interpreters agree on fixtures; fold/interpreter totality.

## Canonical boundary artifact

Use when a boundary requires free syntax, coherent observations, transported semantics, lifted implementations, pullback witnesses, pushout integration, explicit IR, or residual obligations. Laws depend on the artifact: preservation, coherence, agreement, factorization, projection, lowering, or interpreter equivalence.

## Freyd / premonoidal category

Use when pure values and effectful computations share types but order is observable. Laws: pure embedding preserves identity/composition; central operations commute; effect reordering requires observational commutativity.

## Colored operad

Use when typed components assemble hierarchically and a composite remains a component. Laws: port typing, identity wiring, associative substitution, and semantic interpretation preserving substitution.

## PROP / properad / traced structure

Use when multiple outputs or feedback are fundamental rather than conveniently bundled. Laws: network composition/feedback preserves the chosen semantic observations and resource constraints.
