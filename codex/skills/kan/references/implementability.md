# Implementability guide

| Setting | Strategy | Witness |
|---|---|---|
| finite `Set` categories | build comma categories; compute quotients/products | Python finite model |
| posets/lattices | joins for `Lan`, meets for `Ran`, residuals for lifts | policy/build status |
| Haskell-like types | existential `Lan`, rank-n `Ran`, codensity, Yoneda/Coyoneda | type witness |
| mainstream architecture | interfaces, adapters, first-order IR, law tests | module-boundary witness |
| database schemas | `Σ = Lan`, `Δ`, `Π = Ran`; lift-shaped view updates | migration tests |

## Extension algorithms

`Lan_K F(d)`:

1. enumerate `K ↓ d`;
2. create tagged payloads `(c, u : Kc -> d, x ∈ F c)`;
3. quotient by source morphisms;
4. implement `η` as identity-path injection.

`Ran_K F(d)`:

1. enumerate `d ↓ K`;
2. build families over all observations;
3. keep only coherent families;
4. implement `ε` as identity-observation projection.

## Lift approximations

For poset-shaped architecture:

```text
left lift:  least b with F(a) <= P(b)
right lift: greatest b with P(b) <= F(a)
```

Always state the order/refinement relation.

## Freyd/AFT practice

For `P : B -> C`, check:

- `B` can combine/solve constraints relevant to the refactor;
- `P` preserves those constraints in tests;
- each requirement class has bounded implementation templates;
- candidate `Free : C -> B` has a projection law.

## Practical constraints

- Quotients need normalization or opaque smart constructors.
- Limits/coherence need validators and explicit failures.
- Defunctionalized IR needs an escape hatch if the extension point is intentionally open.
- Mainstream code rarely proves universal properties; use law tests and source discipline.
