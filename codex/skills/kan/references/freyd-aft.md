# Freyd adjoint-functor theorem practice

## Role in this skill

Freyd's adjoint functor theorem (AFT) is not a replacement for Kan extensions or Kan lifts. Use it as a **boundary diagnostic**:

```text
Kan lift: identify the outside-in architecture problem.
Freyd/AFT: test whether the projection boundary is disciplined enough to admit a canonical free implementation builder.
```

When a lift-shaped refactor has

```text
A --?--> B
|        |
F        P
v        v
C
```

ask whether the projection `P : B -> C` behaves like a right adjoint candidate. If it does, there may be a free builder

```text
Free : C -> B
Free ⊣ P
```

and the lift candidate becomes:

```text
L = Free · F : A -> B
```

This turns an outside-in refactor into a disciplined construction:

```text
external commitment -> observable behavior -> canonical internal realization
A --F--> C --Free--> B
```

## CS reading of the theorem

A standard general adjoint functor theorem says: a functor `P : B -> C` that is continuous/limit-preserving, has a complete locally small domain, and satisfies a solution-set condition is a right adjoint, so it has a left adjoint. Sources: `[KAN-RIEHL-CTIC]`, `[KAN-NLAB-AFT]`.

Software reading:

```text
If a projection/forgetful/observation API preserves constraint structure,
and the implementation world can solve the relevant constraints,
and every observable behavior has a bounded menu of implementation templates,
then a canonical free implementation builder is plausible.
```

Do not claim a software boundary satisfies Freyd's theorem unless the categories, functors, limits, and solution-set condition have actually been modeled. In ordinary codebase work, use this as an architecture inference and test discipline.

## Freyd/AFT boundary diagnostic

Run this diagnostic after identifying a lift-shaped refactor.

### 1. Name the projection `P`

`P : B -> C` must be a concrete boundary, not a vibe.

Examples:

- controller/service runtime projected to HTTP responses;
- internal workflow projected to audit/event traces;
- database schema projected to public reports;
- implementation module projected to contract-test observations;
- effect handler projected to runtime behavior;
- internal model projected to legacy client DTOs;
- compiler IR projected to generated code or diagnostics.

If `P` is scattered across controllers, serializers, logging hooks, and test helpers, first refactor toward a central projection module before relying on lift reasoning.

### 2. Check the implementation world `B`

Ask whether `B` has enough constraint-solving structure for the refactor.

Architecture analogues of limits:

- products: combine capabilities or modules;
- pullbacks: join two components over a shared interface;
- equalizers: enforce that two observations agree;
- intersections/meets: combine requirements or policies;
- constraint objects: represent compatibility conditions explicitly;
- validation objects: carry success/failure and evidence.

If `B` cannot represent the conjunction of two requirements, a free builder behind `P` is unlikely to be meaningful.

### 3. Check whether `P` preserves constraints

`P` should not destroy the compatibility structure needed by the refactor.

Test analogues:

```text
project(combine(x, y)) behaves like combine(project(x), project(y))
project(equalized(x)) satisfies observed equality
project(pullback over shared interface) agrees on shared observation
```

For code, use regression tests or golden fixtures rather than theorem language.

### 4. Check solution-set-like bounded templates

The solution-set condition is the most useful architecture idea. For each observable requirement, there should be a small family of implementation templates through which all accepted implementations factor.

Examples:

```text
idempotency:
  database key table | event dedupe | external idempotency provider | replay cache

authorization:
  local policy | external policy engine | capability token | role matrix

workflow:
  synchronous call | state machine | saga | effect handler | queue worker

read model:
  direct query | materialized view | event projection | cached projection
```

If the candidate implementation space is open-ended and unbounded, the architecture is not ready for a canonical free builder. Emit an obstruction report instead.

### 5. Propose the free builder

If the checks pass, define a candidate builder:

```text
Free : C -> B
```

In code, this might be:

- `buildWorkflowFromContract`;
- `synthesizeServicePlan`;
- `buildEffectProgram`;
- `generateImplementationSkeleton`;
- `buildProjectionRealizer`;
- `freeDslFromSignature`;
- `freeCategoryFromGraph`;
- `freePolicyFromRequirement`.

Then set:

```text
L = Free · F
```

and write a law test:

```text
project(Free(required_behavior)) satisfies required_behavior
```

## Exactness classifications

A free builder often gives a generated or covering object rather than literal equality. Classify the unit-like comparison:

- exact: `P(Free(c)) == c`;
- embedding: `c -> P(Free(c))` embeds generators into generated behavior;
- covering: `P(Free(c))` contains at least the required behavior;
- sound: `P(candidate)` stays within allowed behavior;
- approximate: relation is documented and tested modulo normalization;
- no-exact-lift: current `B` and `P` cannot realize required observations.

Use the chosen classification consistently in tests.

## Relationship to Kan lifts

Global Kan lifts are adjoints to postcomposition by `P`. Freyd/AFT gives conditions under which adjoints exist. Architecturally:

```text
postcomposition by P = run implementation and observe it
Kan lift             = solve backward through that observation boundary
Freyd/AFT            = test whether P is good enough to have a canonical free side
```

Use this combined practice when the codebase has strong external commitments and you need internals to be rebuilt around those commitments.

## Failure modes

- Vague projection: `P` is not centralized or testable.
- Constraint loss: `P` hides distinctions required by `F`.
- Missing templates: no bounded family of implementation strategies covers the requirement.
- False exactness: a generated implementation covers the spec but does not equal it.
- Overclaiming: treating an architecture heuristic as a theorem without explicit categories.
- Unlawful builder: `Free` is implemented by ad hoc casework with no projection law.

## Minimal output template

```text
Lift data:
- A:
- B:
- C:
- P : B -> C:
- F : A -> C:

Freyd/AFT diagnostic:
- structure forgotten/observed by P:
- constraints available in B:
- constraints preserved by P:
- solution-set-like templates:
- candidate Free : C -> B:
- candidate L = Free · F:
- exactness classification:
- law test:
- obstruction if any:
```
