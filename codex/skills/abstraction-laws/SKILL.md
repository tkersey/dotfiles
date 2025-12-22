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

## Evidence gathering workflow
1. Locate 3+ instances that look similar and record file:line.
2. For each instance, capture inputs, outputs, and error handling.
3. Outline the data/control flow in 1-2 lines per instance.
4. Note the caller's intent (why it exists, not how it works).

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

## Partial-match lane
If only 2 steps are shared (or one step diverges), extract a small helper or shared data type instead of a full abstraction. Revisit only after a third instance appears.

## Seam test rubric
Answer yes/no to each:
1. Can callers use the abstraction without knowing the concrete variant?
2. Can you describe the abstraction in one sentence without naming any current implementation?
3. Would new instances fit without new flags or conditionals?
If any answer is "no," prefer a smaller helper or keep duplication.

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
Only run this pass if algebraic cues are present (map/fold/compose, identity/associativity, combine/merge ops). Otherwise, skip.

Map to the simplest construction:
- Product / record for shared fields.
- Coproduct / tagged union for alternatives.
- Monoid / semigroup for combine operations.
- Functor/applicative/monad only if you can state and test laws.

## Law-based check
Pick one quick test and make it executable:
- Identity: op(x, identity) == x
- Associativity: op(a, op(b, c)) == op(op(a, b), c)
- Functor identity: map(id, x) == x
- Functor composition: map(f, map(g, x)) == map(f∘g, x)
Verification guidance:
- Prefer a property test if the repo has a property framework.
- Otherwise, add 3 representative cases + 1 edge case.
- Place the check in the closest existing test file for the module.

## Worked example (mini)
```
| Instance | Location | Shared Shape            | Variance Point        |
|----------|----------|-------------------------|-----------------------|
| A        | foo:10   | parse -> validate -> save | save target (db/file) |
| B        | bar:42   | parse -> validate -> save | validation rules      |
| C        | baz:88   | parse -> validate -> save | error mapping         |

Verdict: essential (domain pipeline)
Name: ingest-and-persist
Fixed parts: parse -> validate -> save
Variance points: validator, saver, error mapper
Break-glass: if a new flow skips validation entirely, abandon and split
Law check: identity for "no-op validator" preserves input (3 cases + 1 edge)
```

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
