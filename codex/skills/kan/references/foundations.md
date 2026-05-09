# Kan foundations

## Extensions

A left Kan extension of `F : C -> E` along `K : C -> D` is `Lan_K F : D -> E` with unit

```text
η : F -> Lan_K F · K
```

and universal bijection:

```text
Nat(Lan_K F, G) ≅ Nat(F, G · K)
```

A right Kan extension is `Ran_K F : D -> E` with counit

```text
ε : Ran_K F · K -> F
```

and universal bijection:

```text
Nat(G, Ran_K F) ≅ Nat(G · K, F)
```

When both exist for fixed `K`:

```text
Lan_K ⊣ K* ⊣ Ran_K
```

where `K*` is precomposition/restriction. Sources: `[KAN-RIEHL-CTIC]`, `[KAN-MACLANE-CWM]`.

## Pointwise formulas

```text
(Lan_K F)(d) ≅ colim(K ↓ d -> C -> E)
(Ran_K F)(d) ≅ lim(d ↓ K -> C -> E)
```

Set-valued formulas:

```text
(Lan_K F)(d) ≅ ∫^c D(Kc,d) × F(c)
(Ran_K F)(d) ≅ ∫_c F(c)^(D(d,Kc))
```

Engineering reading:

- `Lan`: generated pieces `(path Kc -> d, payload F c)` modulo source equations.
- `Ran`: coherent families of observations indexed by `(path d -> Kc)`.

## Lifts

For a fixed projection `P : B -> C`, postcomposition sends `G : A -> B` to `P · G : A -> C`.

When adjoints exist:

```text
Lft_P ⊣ P_* ⊣ Rft_P
```

This skill uses local notation `Lft_P` and `Rft_P`. Sources: `[KAN-NLAB-LIFT]`.

## Freyd/AFT in this skill

Freyd/AFT is used as a boundary diagnostic: a well-behaved projection `P : B -> C` may admit a free builder `Free : C -> B`. In codebase work, treat this as an engineering inference unless the theorem hypotheses are modeled. Sources: `[KAN-RIEHL-CTIC]`, `[KAN-NLAB-AFT]`.
