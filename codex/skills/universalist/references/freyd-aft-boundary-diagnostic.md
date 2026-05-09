# Freyd/AFT Boundary Diagnostic

This is a Track D sub-practice for lift-shaped architecture. It is not a request to teach Freyd's adjoint functor theorem in full.

## Operational slogan

```text
Lift identifies the outside-in refactor.
Freyd/AFT diagnoses whether the projection can support a canonical free builder.
```

Given:

```text
A --?--> B
|        |
F        P
v        v
C        C
```

Ask:

```text
Is P : B -> C a well-behaved observation/forgetful projection?
Can required behavior in C be freely/canonically realized in B?
```

## Software reading of the theorem's conditions

| Theorem-flavored condition | Software reading |
| --- | --- |
| `B` has enough limits/constraint structure | internals can combine requirements, express equality, validate overlap, compose workflows, or join views |
| `P` preserves limits/constraints | observing after combining internals agrees with combining observations |
| solution-set condition | each public behavior has a bounded menu of implementation templates |
| left adjoint/free builder exists | there is a canonical builder `Free : C -> B` or a principled realizer/obligation artifact |

## Diagnostic checklist

1. Name `P` in code: serializer, controller runner, test harness, report view, trace observer, projection, or forgetful API.
2. Name what `P` forgets or erases.
3. Name the constraints in `B` that matter.
4. Check whether `P` preserves those constraints.
5. List implementation templates for each public requirement.
6. Propose `Free`, `realize`, or `deriveObligations`.
7. Classify the law: exact, covering, sound, or approximate.
8. Add an obstruction if no exact/free lift exists.

## Output shape

```text
Projection P:
What P forgets:
Required behavior F:
Candidate builder Free:
Template family:
Constraint preservation check:
Law/proof signal:
Obstruction:
```

## Proof signals

Exact:

```text
project(free(required(case))) == required(case)
```

Covering:

```text
required(case) embeds into project(free(required(case)))
```

Sound:

```text
project(free(required(case))) satisfies required(case)
```

Obstruction:

```text
no exact lift because P discards <evidence> or B lacks <constraint/template>
```

## Guardrail

Use the diagnostic only when it changes code shape, tests, or migration risk. Otherwise it is category-theory cosplay.
