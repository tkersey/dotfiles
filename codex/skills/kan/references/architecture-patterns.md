# Architecture patterns

## Plugin API as `Lan`

`C`: core AST. `D`: plugin surface. `K`: core inclusion. `F`: old interpreter.

Use `Lan` to generate/default plugin behavior while preserving old semantics.

Law: `newEval(embed(oldExpr)) == oldEval(oldExpr)`.

## Compatibility facade as `Ran`

`C`: legacy observations. `D`: new model. `F`: legacy behavior.

Use `Ran` to build coherent old-client projections from the new model.

Law: overlapping projections commute.

## Contract-first refactor as lift

`A`: contract cases. `B`: internal architecture. `C`: public behavior. `P`: runtime projection. `F`: required behavior.

Use lift reasoning to find `L : A -> B` with `P(L(a)) ~= F(a)`.

## Freyd/AFT projection diagnostic

If the lift depends on `P`, ask whether `P` supports a free builder:

```text
Free : C -> B
L = Free · F
```

Check constraints in `B`, preservation by `P`, and bounded implementation templates.

## Category-driven layout

```text
core/          C, F, old semantics
boundary/      K or P, units/counits/comparisons
generated/     Lan/free artifacts
facade/        Ran views
lift/          realizers, obligations, free builders
ir/            defunctionalized observations/paths/requirements
laws/          projection and naturality tests
```
