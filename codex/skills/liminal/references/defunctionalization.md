# Defunctionalization

## Table of Contents

1. Canonical algorithm
2. Source split
3. Typed and modular variants
4. Functional correspondence
5. Engineering heuristics

## Canonical algorithm

The base transformation replaces higher-order function values with:

- a finite set of first-order constructors carrying the function's free variables
- a single `apply` dispatcher or equivalent case split

Minimal mental model:

```text
Before:
let f = (lambda x. x + n) in f 10

After:
data Fun = F_AddN(n)
apply(F_AddN(n), x) = x + n
let f = F_AddN(n) in apply(f, 10)
```

Use this transformation vocabulary when the user asks to:

- first-orderize an interpreter
- expose hidden control flow
- derive an abstract machine
- replace closures with concrete data

## Source split

- `[DEF-REYNOLDS-1972]`: definitional-interpreter origin story and constructive variation between interpreter styles.
- `[DEF-DN-2001]`: the canonical citation for defunctionalization as a whole-program higher-order to first-order transformation.
- `[DEF-AGER-2003]`: evaluator-to-machine correspondence, including closure conversion, CPS, and defunctionalization.
- `[DEF-REFUNC-2007]`: how to move back from defunctionalized machine structure to higher-order interpreters.

## Typed and modular variants

Mention the variant that matches the problem:

- `type-driven defunctionalization`: when preserving typability is central; cite `[DEF-DN-2001]` for the core transform and `[DEF-DT-2023]` when the type-preservation proof itself is central
- `polymorphic typed defunctionalization`: when constructor explosion or polymorphism matters
- `modular defunctionalization`: when separate compilation is part of the constraint
- `dependent-type defunctionalization`: when ordinary closure encodings break proof obligations; use `[DEF-DT-2023]`
- `mechanized typed control`: when the user wants a checked artifact around multiple control operators; use `[TYPE4D-2022]` and `[TYPE4D-ARTIFACT]`

## Functional correspondence

The standard evaluator-to-machine story is:

```text
definitional evaluator
-> closure conversion when functions and environments must be made explicit
-> CPS transformation
-> defunctionalized continuations
-> abstract machine
```

Use this chain when the user wants to derive a machine instead of inventing one.
Use `[DEF-AGER-2003]` when the closure-conversion step matters.
Name refunctionalization when the prompt asks how to move back from a machine to a higher-order interpreter.

## Engineering heuristics

- trim constructor payloads to the free variables actually used
- localize `apply` cases when inlining and branch prediction matter
- watch for polymorphism-driven constructor growth
- pair defunctionalization with CPS only when the goal is explicit control structure, not merely closure conversion

Use `[DEF-DN-2001]` for the transformation itself, `[DEF-AGER-2003]` for machine derivation, and `[DEF-REFUNC-2007]` when the question is really about recovering the higher-order structure.
