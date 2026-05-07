# Kan repo audit memo template

## Current architecture sketch

- Core domain:
- Target/new surface:
- Current adapters/generators:
- Duplicated semantics:
- Existing compatibility tests:

## Candidate Kan data

```text
C:
D:
K:
F:
E:
Direction:
η or ε:
Witness d:
```

## Where the analogy holds

- Objects:
- Morphisms:
- Functorial action:
- Unit/counit in code:

## Where it breaks

- Missing morphism mapping:
- No quotient/coherence support:
- Untestable universal property:
- Plain interface is enough:

## Refactor plan

1. Centralize `η`/`ε` adapter.
2. Add witness law test.
3. Move duplicated semantics behind the adapter.
4. Add golden tests for old behavior.
5. Only then introduce `Lan`/`Ran` naming in code/docs.
