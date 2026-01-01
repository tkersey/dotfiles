---
name: abstraction-laws
description: "Law-driven abstraction protocol: evidence first, seam test, minimal algebra, executable law check."
---

# Abstraction Laws

## When to use
- You see the same code shape in 3+ places and want to unify it.
- Refactors stall on “how general should this be?”.
- Parameter clusters repeat across modules.
- Algebraic cues show up (map/fold/compose, identity/associativity, combine/merge ops).

## Quick start
1. Collect 3+ concrete instances (file:line).
2. Classify similarity: essential (domain) vs accidental (incidental implementation).
3. Run the seam test (can callers stay ignorant of the concrete variant?).
4. Name the abstraction by behavior.
5. If algebraic, pick the minimal construction and add one executable law check.

## Evidence table
```
| Instance | Location | Shared Shape | Variance Point |
|----------|----------|--------------|----------------|
| A        | file:line| ...          | ...            |
| B        | file:line| ...          | ...            |
| C        | file:line| ...          | ...            |
```

## Essential vs accidental
- Essential: the shared shape exists because of domain rules.
- Accidental: the shared shape exists because of today’s implementation.
- If accidental, prefer duplication (or a smaller helper) until the domain forces convergence.

## Seam test (yes/no)
1. Can callers use the abstraction without knowing the concrete variant?
2. Can you describe it in one sentence without naming a current implementation?
3. Would a new instance fit without adding flags or branching?

If any answer is “no”, extract a smaller helper or keep duplication.

## Abstraction template
```
Name: <behavioral name>
Fixed parts:
- ...
Variance points:
- ...
Interface sketch:
- ...
Break-glass:
- <next likely change that makes this harmful>
```

## Universalist pass (only if algebraic)
Map to the smallest construction:
- Product (record/struct) for independent fields
- Coproduct (tagged union) for alternatives
- Semigroup/monoid for combine operations
- Functor/applicative/monad only if you can state and test the laws

## Law check (make it executable)
Pick one and implement it where the repo can run it:
- Identity: `op(x, identity) == x`
- Associativity: `op(a, op(b, c)) == op(op(a, b), c)`
- Functor identity: `map(id, x) == x`
- Functor composition: `map(f, map(g, x)) == map(compose(f, g), x)`

Verification:
- Prefer property tests if the repo already has them.
- Otherwise add a small set of representative cases (include an edge case).

## Deliverable format
- Evidence table (3+ instances).
- Essential vs accidental verdict.
- Proposed abstraction (fixed vs variance points) + break-glass scenario.
- One executable law check.

## Activation cues
- "this looks like that"
- "duplicate pattern"
- "shared shape"
- "extract abstraction"
- "monoid/fold/compose"
