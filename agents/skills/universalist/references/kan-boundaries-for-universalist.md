# Kan Boundaries for Universalist

Consult this reference for a task-grounded Kan hypothesis or a question about
transporting semantics through a map or realizing them behind a projection.
An ordinary construction need not fail before the theory can help formulate the
question. Compare native realizations when recommending a construction.

## Extension-shaped boundary

```text
C --K--> D
|        |
F        ?
v        v
E        E
```

Software reading:

- `C`: source/core/legacy world.
- `D`: target/ambient/new world.
- `K`: embedding, schema map, API version map, AST embedding.
- `F`: old semantics, interpreter, data instance, behavior.
- `?`: target-side semantics.

Use left-Kan-style language when behavior should be freely/generatedly transported.
Use right-Kan-style language when behavior should be determined by coherent observations.

## Lift-shaped boundary

```text
A --?--> B
|        |
F        P
v        v
C        C
```

Software reading:

- `A`: public cases, contract tests, workflows, or requirements.
- `B`: internal implementation world.
- `C`: observable public behavior.
- `P`: projection from internals to public behavior.
- `F`: required public behavior.
- `?`: implementation realizer or residual obligations.

Use lift language when the question is: what must exist behind this fixed projection?

## Universalist rule

Do not let Kan vocabulary substitute for the relevant diagram, comparison cells,
hypotheses, and universal property. Recognition can finish with an established
correspondence, consequences, and limits. For a proposed realization, identify:

- boundary artifact;
- constructor/interpreter/projection;
- one witness seam;
- one proof signal.

When the stronger claim is unsupported, report the supported weaker correspondence
or unresolved premise. An ordinary adapter may be adequate without possessing a
Kan universal property; a missing new artifact does not refute an existing one.
