# Possibility Sheafification

## Core idea

A codebase already contains local evidence about what an abstraction means. The evidence is distributed across call sites, tests, controllers, serializers, database constraints, UI assumptions, adapters, policy checks, event handlers, context compilers, and generated artifacts.

Possibility Sheafification treats that evidence as a site:

```text
patches        = local usage contexts
local sections = local meanings of the abstraction
overlaps       = shared fields, IDs, traces, fixtures, observations, constraints
global section = the intended abstraction
```

An architecture-level abstraction is exact when compatible local meanings glue to one global meaning, and that gluing is unique up to intended equivalence.

```text
compatible local meanings glue uniquely to global meaning
```

## What it manipulates

Possibility Sheafification manipulates abstractions by comparing their **possibility envelope** to their real usage site.

- Too broad: admits impossible global states.
- Too narrow: cannot represent compatible local meanings.
- Redundant: several global states have the same local observations.
- Inconsistent: local sections disagree on overlaps.
- Misplaced: the global meaning is hidden in a callback, serializer, test, or adapter.

## Four failures

### Local inconsistency

Local meanings disagree on an overlap. Repair with refined states, split abstractions, equalizers, pullbacks, coherent observations, or obstruction reports.

### Missing global glue

Local meanings are compatible but no global artifact represents them. Repair with free syntax, effect signature, lifted implementation, context schema, realizer, or obligation artifact.

### Non-unique gluing

Multiple global representations produce the same local behavior. Repair with quotient, canonicalization, normal form, coequalizer-like artifact, or a single interpreter/projection.

### Hidden excess possibility

The global abstraction admits states that no local behavior can justify. Repair with coproducts, refined types, state machines, behavioral coalgebras, exact context constraints, or defunctionalized IR.

## Workflow

1. Name the abstraction and files.
2. Build the usage site: local contexts that cover the abstraction.
3. Extract local sections: what each context believes the abstraction means.
4. Identify overlaps: shared keys, observations, traces, fields, tests, invariants.
5. Check compatibility on overlaps.
6. Check existence of global glue.
7. Check uniqueness of global glue.
8. Classify the sheaf failure.
9. Select the canonical repair.
10. Emit a Sheafification Certificate.
11. Add one gluing law and one falsifier.
12. Refactor one witness slice and stop.

## Canonical repairs

| Sheaf failure | Architecture smell | Canonical repair |
|---|---|---|
| Local disagreement | semantic drift | split/refine/equalize |
| Compatible locals lack global | missing artifact | free syntax, Kan lift, effect signature, context schema |
| Multiple globals same locals | redundant representation | quotient, canonicalization, normal form |
| Global admits invisible states | overbroad abstraction | refined type, sum type, state machine |
| Local callbacks cannot be compared | hidden behavior | defunctionalized IR |
| Local observations scattered | projection sprawl | Yoneda observation vocabulary |
| Generated locals lack provenance | arbitrary generation | Coyoneda payload + path |
| Public behavior determines internals | outside-in pressure | Kan lift / residual obligations |
| Ongoing behavior over time | trace/protocol pressure | behavioral coalgebra |
| Consumer sees raw source data | uncertified context | Exact Context / Context Certificate |

## Guardrail

Do not sheafify local helpers or intentionally open extension points. Use Possibility Sheafification when the abstraction is architecture-level and local usage evidence shows an exactness gap.
