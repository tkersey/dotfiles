# Freyd Categories for Effectful Call-by-Value

Use `freyd-category` mechanics when pure values and effectful computations share types but have different composition laws. Do not confuse this with `freyd-aft`, which asks whether a projection supports a free left adjoint/builder.

## Structure

A Freyd-category presentation consists operationally of:

```text
C = pure category, usually cartesian/monoidal
K = effectful computation category, premonoidal
J : C -> K = identity-on-objects pure embedding
```

Pure morphisms are **central**: they commute with surrounding effects. General effectful morphisms need not satisfy interchange, so evaluation order remains observable.

## Software reading

```text
C:
  validation, normalization, calculation, plan construction, static policy

K:
  database writes, network calls, clock/randomness, filesystem/tool operations,
  audit emission, state mutation, exceptions, nondeterminism

J:
  lift a pure transformation into effectful execution
```

Use when:

- call-by-value sequencing matters;
- a `Promise`/`IO`/effect wrapper hides ordering semantics;
- parallelization or reordering is proposed without commutativity proof;
- pure and effectful code are mixed but should share types/interfaces;
- values must be threaded through computations explicitly.

## Strong-monad relation

A strong monad supplies a standard Freyd category through its Kleisli category. The Freyd presentation is more primitive for first-order architecture; representability/closedness conditions are needed before every such presentation becomes a strong-monad implementation.

## Required report

```text
Pure world/category:
Effectful world/category:
Pure embedding J:
Shared objects/types:
Context action / value threading:
Evaluation order:
Central operations:
Claimed commuting/parallel operations:
Noncommuting counterexample:
Higher-order representation requirement:
```

## Laws

```text
J(id) = id
J(g . f) = J(g) . J(f)
pure operations commute with effectful context
claimed effect reordering requires observational commutativity
```

## Falsifiers

- reordering two accepted computations changes trace/result/state;
- an operation labeled pure performs hidden effects;
- a supposedly central operation fails to commute;
- parallel composition duplicates/discards a resource without a law.

Sources: `[POWER-ROBINSON-PREMONOIDAL]`, `[POWER-THIELECKE-FREYD]`.
