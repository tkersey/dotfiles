# Universal Architecture Kernel

Universal architecture is the practice of designing software around canonical boundary artifacts and, when locality or indexing is semantic, explicit structure inside worlds and their description categories.

Central rule:

```text
Primitive operations may be arbitrary.
Composition boundaries may not be arbitrary.
Local context may not be implicit when it changes correctness.
The composition of descriptions may not be invented independently of their indices.
```

Ordinary code may live inside a boundary: I/O, arithmetic, parsing, database drivers, vendor APIs, ML inference, clocks, randomness, local algorithms. The boundary where such code composes with other worlds should be explicit and testable.

## Kernel artifacts

1. **Worlds**
   - Domain, API, DB, events, UI, runtime, compiler IR, policy, tests, observability.

2. **Boundaries**
   - Embeddings, projections, handlers, interpreters, serializers, compilers, views, report extractors.

3. **Free syntax**
   - ASTs, commands, workflows, effect programs, query languages.

4. **Coherent observations**
   - Sanctioned projections, old client views, report observations, policy queries.

5. **Transported semantics**
   - Old behavior moved to new target surfaces through explicit paths.

6. **Lifted implementations**
   - Public behavior determines internal realizer or implementation template.

7. **Free builders behind projections**
   - A disciplined observation boundary supports canonical construction back into implementation space.

8. **Obstruction reports**
   - The projection loses evidence, internal constraints cannot combine, templates are unbounded, required locality has no effective presentation, or description decompositions/quotients are non-effective.

9. **Behavioral coalgebras**
   - Ongoing behavior specified by transition plus observation.

10. **Effect signatures and handlers**
    - Operation syntax separated from runtime interpretation.

11. **Base composition geometry**
    - Categories, monoidal/Freyd structures, operads, PROPs, traced structures, and resource-sensitive worlds make legal composition explicit.

12. **Description composition**
    - Pointwise, Day, promonoidal, substitutional, or monadic products are selected separately for functors, presheaves, predicates, plans, graded families, rules, contexts, or spatial descriptions indexed by a world.

13. **Day/promonoidal convolution**
    - Base composition is lifted to indexed descriptions through legal decomposition witnesses, coherent quotienting, lax-monoidal interpretation, and effective enumeration/normalization.

14. **Comonadic spatiality**
    - Points have coherent local neighborhoods; density comonads generate locality from patches; coalgebras represent situated objects; halos and germs expose local context; continuous boundaries preserve required locality.

15. **Effective spatial presentations**
    - Finite, bounded, indexed, or queryable halos; explicit local/global identity; labelled relationships; basis/reconstruction or non-basis obstruction; invalidation and resource laws.

16. **Spatial convolution**
    - External-product patch systems compose suitable spatial descriptions while retaining halo labels, continuous projections, and effective maintenance.

17. **Explicit IR**
    - Callbacks, handlers, continuations, predicates, mappers, and rules become data plus interpreter.

18. **Law tests**
    - Executable witnesses for construction, observation, projection, lowering, transition, handler, interpreter, decomposition, quotient, representable preservation, center/coherence, restriction, density, or continuity laws.

## Operating test

A proposed universal artifact, spatial structure, or description product is legitimate only if it changes at least one of:

- code shape;
- module boundary;
- artifact provenance;
- index/grade/resource representation;
- legal decomposition or admissibility representation;
- local/global identity handling;
- dependency, ownership, capability, evidence, or context representation;
- central interpreter/projection/handler/context transport;
- static analysis, cost analysis, documentation, or multi-interpreter support;
- test suite;
- ability to reject invalid states/paths/obligations/locality violations/illegal decompositions;
- ability to prevent bypasses;
- impact/invalidation/resource accounting.

A plain dependency graph or context wrapper remains preferable when it satisfies the required observations without comonad, basis, halo, or continuity claims. A product, pointwise map, operadic substitution, monadic program, pullback, or pushout remains preferable when it already expresses the intended description composition without Day/promonoidal mechanics.
