# Boundary: `kan` vs `algebra-driven-design`

Use this boundary when both skills appear plausible.

## Use `algebra-driven-design` when the governing question is domain algebra

Choose ADD when the task asks for:

- carriers and valid/invalid states
- operations and signatures
- observations that define equality
- laws, non-laws, policy laws, and counterexamples
- reducers, event streams, commands, effects, and interpreters
- property, parity, trace, scenario, contract, or runtime law tests
- architecture derived from domain laws

Prompt examples:

```text
Use algebraic laws to design the payment lifecycle.
Find the carriers, operations, observations, laws, and non-laws for this cart refactor.
Design an agentic workflow from operations, tool contracts, state, approvals, and validation laws.
```

## Use `kan` when the governing question is a boundary equation

Choose `kan` when the task asks for:

- `Lan_K F`, `Ran_K F`, or restriction along `K`
- `Lft_P F`, `Rft_P F`, or projection through `P`
- compatibility facades, generated target semantics, plugin extension surfaces, or schema/data migration as boundary problems
- implementation synthesis behind a fixed public boundary
- residual requirements or obligations behind a projection
- defunctionalized boundary IR
- Yoneda/Coyoneda observation or deferred-generation boundaries
- categorical witness slices and law tests

Prompt examples:

```text
Audit whether this adapter boundary is a right Kan extension.
Derive internal implementation behind a fixed public API projection.
Replace boundary callbacks with first-order IR and law tests.
```

## Composition rule

If both apply:

1. Use ADD first when the domain laws are not yet known.
2. Use `kan` first when the boundary map/projection is already the central problem.
3. Let ADD provide the domain laws that `kan` later turns into boundary witnesses.
4. Let `kan` provide boundary representation when ADD identifies duplicated observations, generated semantics, or implementation-behind-projection pressure.
