# Universal Architecture Kernel

Universal architecture is the practice of designing software around canonical boundary artifacts.

Central rule:

```text
Primitive operations may be arbitrary.
Composition boundaries may not be arbitrary.
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
   - The projection loses evidence, internal constraints cannot combine, or templates are unbounded.

9. **Behavioral coalgebras**
   - Ongoing behavior specified by transition plus observation.

10. **Effect signatures and handlers**
   - Operation syntax separated from runtime interpretation.

11. **Explicit IR**
   - Callbacks, handlers, continuations, predicates, mappers, and rules become data plus interpreter.

12. **Law tests**
   - Executable witnesses for construction, observation, projection, lowering, transition, handler, or interpreter laws.

## Operating test

A proposed universal artifact is legitimate only if it changes at least one of:

- code shape;
- module boundary;
- artifact provenance;
- central interpreter/projection/handler;
- test suite;
- ability to reject invalid states/paths/obligations;
- ability to prevent bypasses.
