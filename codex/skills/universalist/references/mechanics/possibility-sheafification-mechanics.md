# Possibility Sheafification Mechanics

Use this reference when a Universalist Track G handoff has identified an inexact abstraction.

## Required data

- Abstraction name and files.
- Usage site: local contexts that cover it.
- Local sections: each context's local meaning.
- Overlaps: shared keys, fields, observations, traces, fixtures, invariants.
- Sheaf failure: local inconsistency, missing global glue, non-unique gluing, hidden excess possibility.
- Candidate repair and witness law.

## Repair mechanics

| Failure | Categorical repair mechanics |
|---|---|
| Local inconsistency | equalizer, pullback, refined type, coherent observation, obstruction report |
| Missing global glue | free object, initial algebra, algebraic effect signature, Kan lift, free builder, context schema |
| Non-unique gluing | coequalizer, quotient, normalization, canonical representative, observational equivalence |
| Hidden excess possibility | coproduct, refined type, dependent constraint, state machine, behavioral coalgebra |
| Hidden higher-order locals | defunctionalization: constructors plus apply/interpreter |
| Observation sprawl | Yoneda/Ran observation vocabulary |
| Generation/provenance drift | Coyoneda/Lan generated payload plus path |

## Law shapes

Compatibility law:

```text
restrict(local_i, overlap_ij) == restrict(local_j, overlap_ij)
```

Existence law:

```text
compatible local family -> global replacement value
```

Uniqueness/normalization law:

```text
same local observations -> same canonical global representation
```

Falsifier:

```text
local disagreement, missing global case, non-unique representation, or impossible state
```
