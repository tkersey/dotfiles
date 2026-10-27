# Freyd/AFT Boundary Diagnostic

Use this only for lift-shaped Track D refactors.

Shape:

```text
A --?--> B
|        |
F        P
v        v
C        C
```

Software reading:

- `A`: public cases, contract tests, workflows, requirements, or obligations.
- `B`: internal implementation world.
- `C`: observable behavior world.
- `P : B -> C`: projection, serializer, public API runner, trace observer, report extractor, or forgetful API.
- `F : A -> C`: required public behavior.
- `? : A -> B`: realizer, implementation template, free builder output, or residual obligation.

## Diagnostic questions

1. What exactly is `P` in code?
2. What does `P` forget, observe, serialize, erase, or project?
3. Can `B` express combined constraints, equalities, products, pullbacks, validations, or workflow composition?
4. Does `P` preserve those constraints when observed in `C`?
5. Is there a bounded family of implementation templates for each public behavior?
6. What `Free : C -> B`, realizer, or obligation artifact is suggested?
7. Is the unit/projection exact, covering, sound, or approximate?
8. What obstruction prevents a free/lifted implementation?

## Positive artifact: free builder behind projection

Use when `P` is disciplined enough to support a canonical implementation-side builder.

Code shape:

```text
free : RequiredBehavior -> ImplementationTemplate
project : ImplementationTemplate -> PublicBehavior
```

Proof signal:

```text
project(free(required(case))) satisfies required(case)
```

## Negative artifact: obstruction report

Use when no exact/free lift exists.

Common obstructions:

- `P` forgets evidence needed by `F`;
- `B` cannot combine constraints required by `F`;
- templates are unbounded or not enumerable;
- public behavior is inconsistent;
- implementation world lacks the resource/capability.

Proof signal:

```text
required(case) cannot be realized because named evidence/template/constraint is missing
```

Do not recite the theorem in ordinary responses. Translate it into the operational projection diagnostic.
