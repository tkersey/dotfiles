---
name: abstraction-laws
description: Abstraction Archaeologist plus Universalist; use when you see repeated code shapes, parameter clusters, or algebraic structure cues (map/fold/compose, identity/associativity) and need a safe, law-driven abstraction.
---

# Abstraction Laws

## When to use
- You spot the same shape in 3+ places and want to unify it.
- Refactors stall on "how general should this be?"
- Parameter clusters repeat across modules.
- Algebraic cues appear (map/fold/compose, identity/associativity, monoid-like ops).

## Quick start
1. Gather at least 3 concrete instances with file:line.
2. Separate essential vs accidental similarity.
3. Test the seam: can callers use the abstraction without leaking details?
4. Name the abstraction after behavior, not implementation.
5. If algebraic, identify the minimal construction and a law-based check.

## Evidence table
```
| Instance | Location | Shared Shape | Variance Point |
|----------|----------|--------------|----------------|
| A        | file:line| ...          | ...            |
| B        | file:line| ...          | ...            |
| C        | file:line| ...          | ...            |
```

## Essential vs accidental test
- Essential: similarity exists because of domain rules.
- Accidental: similarity exists only due to current implementation.
- If accidental, prefer duplication until the domain forces a shared shape.

## Proposed abstraction template
```
Name: <behavioral name>
Fixed parts:
- ...
Variance points:
- ...
Interface sketch:
- ...
```

## Break-glass scenario
Describe the next likely change that would make this abstraction harmful.
If that scenario is probable, keep the code duplicated.

## Universalist pass
Map to the simplest construction:
- Product / record for shared fields.
- Coproduct / tagged union for alternatives.
- Monoid / semigroup for combine operations.
- Functor/applicative/monad only if you can state and test laws.

## Law-based check
Pick one quick test:
- Identity: op(x, identity) == x
- Associativity: op(a, op(b, c)) == op(op(a, b), c)
- Functor identity: map(id, x) == x
- Functor composition: map(f, map(g, x)) == map(f∘g, x)

## Deliverable format
- Evidence table with 3+ instances.
- Essential vs accidental verdict.
- Proposed abstraction with variance points.
- Break-glass scenario.
- One law-based check.

## Activation cues
- "this looks like that"
- "duplicate pattern"
- "shared shape"
- "extract abstraction"
- "monoid/fold/compose"
