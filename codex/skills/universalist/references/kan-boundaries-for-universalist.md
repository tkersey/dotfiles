# Kan Boundaries for Universalist

Use this only after the ordinary construction ladder is not enough.

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

Never answer with Kan vocabulary alone. Translate it into:

- boundary artifact;
- constructor/interpreter/projection;
- one witness seam;
- one proof signal.

If those cannot be named, downgrade to ordinary universalist construction or plain adapter.
