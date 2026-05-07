# Implementability guide

## Choosing a representation

| Setting | Implementation strategy | Typical witness |
|---|---|---|
| Finite categories, `Set`-valued `F` | Build comma category, compute quotient/product with compatibility | runnable Python model |
| Posets/lattices | Compute joins for `Lan`, meets for `Ran` | policy inheritance, build dependency status |
| Haskell-like typed programs | Rank-n `Ran`, existential `Lan`, `Codensity`, `Density`, Yoneda/Coyoneda | type-level witness |
| TypeScript/Rust/Python architecture | Encode as interfaces, existential packages, callbacks, adapters, law tests | module boundary witness |
| Database schemas | `Σ`/`Δ`/`Π` data migration functors | schema migration test |
| DSL/interpreters | `Lan` for extending syntax/semantics, `Ran` for observational compatibility | AST node/interpreter case |

## Finite `Set`-valued algorithm

Input:

```text
C: finite category
D: finite category
K: functor C -> D
F: functor C -> Set
```

### Pointwise `Lan_K F(d)`

1. Construct the comma category `K ↓ d`.
2. For every object `(c, u : Kc -> d)`, create tagged elements `(c, u, x)` for each `x ∈ F(c)`.
3. For every morphism `f : (c,u) -> (c',u')`, impose the relation:

```text
(c, u, x) ~ (c', u', F(f)(x))
```

4. Return equivalence classes.
5. Unit map:

```text
η_c(x) = [(c, id_{Kc}, x)] in Lan_K F(Kc)
```

### Pointwise `Ran_K F(d)`

1. Construct the comma category `d ↓ K`.
2. Start with the product of all sets `F(c)` indexed by objects `(c, u : d -> Kc)`.
3. Keep only coherent families `x_(c,u)` such that for every morphism `f : (c,u) -> (c',u')`:

```text
F(f)(x_(c,u)) = x_(c',u')
```

4. Counit map:

```text
ε_c(family) = family_(c, id_{Kc})
```

This is runnable for small categories. For large categories it usually becomes a specification for a database query, optimizer, typeclass, or code generator.

## Engineering translations

### `Lan` implementation forms

- generated code from old/core definitions;
- default behavior for new API surface;
- free syntax extension;
- migration that pushes old rows/events into a new schema;
- plugin wrapper that constructs target plugins from core semantics;
- quotient/normalization layer that identifies equivalent constructions.

### `Ran` implementation forms

- compatibility facade determined by old observers;
- read model with coherent projections;
- product/intersection of client requirements;
- coinductive interface;
- policy aggregation where all old policy views must agree;
- codensity/CPS optimization.

## Practical constraints

- Most real repositories do not have literal small categories. Treat modules/interfaces/tests as an engineering model unless categories are explicitly defined.
- Type systems rarely express naturality directly. Use property tests, golden tests, and centralized constructors/projections.
- Quotients are often awkward in mainstream languages. Implement `Lan` with canonicalization, normalization, or an opaque smart constructor.
- Limits are often awkward when observations are partial. Implement `Ran` with explicit failure modes or validation results.
- Existentials require GADTs, trait objects, closures, opaque packages, or erased wrappers depending on language.
- Rank-n types require Haskell or careful interface simulation; in TypeScript/Python they are only approximations.

## Deciding if implementation is worth it

Use Kan-extension implementation when it prevents one of these concrete problems:

- semantic drift between old and new APIs;
- duplicated interpreters;
- inconsistent adapters;
- ad hoc schema migration paths;
- plugin contracts without compatibility tests;
- bind-heavy free structures with measurable overhead;
- unprincipled generation of target artifacts.

Avoid it when a plain interface, adapter, or helper function gives the same guarantees with less machinery.
