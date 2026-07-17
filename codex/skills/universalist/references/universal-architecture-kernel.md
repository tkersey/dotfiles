# Universal Architecture Kernel

Universal architecture is the practice of designing software around canonical boundary artifacts and, when locality is semantic, explicit spatial structure inside worlds.

Central rule:

```text
Primitive operations may be arbitrary.
Composition boundaries may not be arbitrary.
Local context may not be implicit when it changes correctness.
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
   - The projection loses evidence, internal constraints cannot combine, templates are unbounded, or required locality has no effective presentation.

9. **Behavioral coalgebras**
   - Ongoing behavior specified by transition plus observation.

10. **Effect signatures and handlers**
    - Operation syntax separated from runtime interpretation.

11. **Comonadic spatiality**
    - Points have coherent local neighborhoods; density comonads generate locality from patches; coalgebras represent situated objects; halos and germs expose local context; continuous boundaries preserve required locality.

12. **Effective spatial presentations**
    - Finite, bounded, indexed, or queryable halos; explicit local/global identity; labelled relationships; basis/reconstruction or non-basis obstruction; invalidation and resource laws.

13. **Explicit IR**
    - Callbacks, handlers, continuations, predicates, mappers, and rules become data plus interpreter.

14. **Law tests**
    - Executable witnesses for construction, observation, projection, lowering, transition, handler, interpreter, center/coherence, restriction, density, or continuity laws.

## Operating test

A proposed universal artifact or spatial structure is legitimate only if it changes at least one of:

- code shape;
- module boundary;
- artifact provenance;
- local/global identity handling;
- dependency, ownership, capability, evidence, or context representation;
- central interpreter/projection/handler/context transport;
- test suite;
- ability to reject invalid states/paths/obligations/locality violations;
- ability to prevent bypasses;
- impact/invalidation/resource accounting.

A plain dependency graph or context wrapper remains preferable when it satisfies the required observations without comonad, basis, halo, or continuity claims.