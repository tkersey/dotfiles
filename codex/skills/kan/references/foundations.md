# Kan foundations

## Universal property

A **left Kan extension** of `F : C -> E` along `K : C -> D` is a functor `Lan_K F : D -> E` and a natural transformation:

```text
η : F -> (Lan_K F) · K
```

such that, for every `G : D -> E`, composition with `η` gives a natural bijection:

```text
Nat(Lan_K F, G) ≅ Nat(F, G · K)
```

A **right Kan extension** of `F` along `K` is a functor `Ran_K F : D -> E` and a natural transformation:

```text
ε : (Ran_K F) · K -> F
```

such that, for every `G : D -> E`, composition with `ε` gives a natural bijection:

```text
Nat(G, Ran_K F) ≅ Nat(G · K, F)
```

When left and right Kan extensions exist for fixed `K`, they form the adjoint triple:

```text
Lan_K ⊣ K* ⊣ Ran_K
```

where `K*` is precomposition/restriction along `K`. Sources: `[KAN-RIEHL-CTIC]`, `[KAN-MACLANE-CWM]`.

## Pointwise formulas

For each `d ∈ D`, pointwise Kan extensions compute one target object at a time.

Left:

```text
(Lan_K F)(d) ≅ colim( K ↓ d --Π_d--> C --F--> E )
```

Objects of `K ↓ d` are pairs `(c, u : Kc -> d)`. Morphisms `(c,u) -> (c',u')` are morphisms `f : c -> c'` in `C` such that:

```text
u' · Kf = u
```

Right:

```text
(Ran_K F)(d) ≅ lim( d ↓ K --Π_d--> C --F--> E )
```

Objects of `d ↓ K` are pairs `(c, u : d -> Kc)`. Morphisms `(c,u) -> (c',u')` are morphisms `f : c -> c'` in `C` such that:

```text
Kf · u = u'
```

Sources: `[KAN-RIEHL-CTIC]`.

## Set formulas

When `E = Set` and the relevant ends/coends exist:

```text
(Lan_K F)(d) ≅ ∫^c D(Kc, d) × F(c)
(Ran_K F)(d) ≅ ∫_c F(c)^(D(d, Kc))
```

Engineering reading:

- `Lan`: tagged/generated pieces `(path from Kc to d, value in F c)`, quotiented by source morphisms.
- `Ran`: coherent families of observations indexed by `(path from d to Kc)`.

Sources: `[KAN-RIEHL-CTIC]`, `[KAN-MACLANE-CWM]`, `[KAN-MILEWSKI-2017]`.

## Unit and counit as code

Left unit:

```text
η_c : F(c) -> Lan_K F(Kc)
η_c(x) = class(identity_Kc, x)
```

Right counit:

```text
ε_c : Ran_K F(Kc) -> F(c)
ε_c(family) = family_(c, identity_Kc)
```

For finite `Set` implementations, these are concrete constructors/projections.

## Naturality laws

For `f : c -> c'`:

Left unit naturality:

```text
(Lan_K F)(Kf) · η_c = η_c' · F(f)
```

Right counit naturality:

```text
F(f) · ε_c = ε_c' · (Ran_K F)(Kf)
```

These are the first laws to test.

## Universal factorization laws

Left factorization:

Given `α : F -> G · K`, there is a unique `α# : Lan_K F -> G` such that:

```text
α = (α# · K) · η
```

Right factorization:

Given `β : G · K -> F`, there is a unique `β# : G -> Ran_K F` such that:

```text
β = ε · (β# · K)
```

In software, test uniqueness indirectly: assert that all supported client paths use the same central adapter or constructor/projection and cannot bypass it.

## Special cases

### Identity

`Lan_id F ≅ F ≅ Ran_id F`.

### Fully faithful `K`

If `K` is fully faithful and the Kan extension exists, the unit or counit often becomes an isomorphism on the image of `K`. Engineering reading: old behavior can be preserved exactly on old objects.

### Discrete source category

If `C` has no non-identity morphisms:

```text
Lan_K F(d) ≅ coproduct over arrows Kc -> d of F(c)
Ran_K F(d) ≅ product over arrows d -> Kc of F(c)
```

### Posets

If `C`, `D`, and `E` are posets, Kan extensions often compute joins/meets over lower/upper indexing sets:

```text
Lan_K F(d) = join { F(c) | Kc ≤ d }
Ran_K F(d) = meet { F(c) | d ≤ Kc }
```

when the required joins/meets exist.

### One-object categories

One-object categories are monoids. Kan extensions along homomorphisms recover induction/coinduction-like constructions. In programming, this appears in equivariance, actions, and representation changes.

## Density and codensity

The density monad/comonad and codensity monad arise from Kan-extension constructions. In programming, codensity is the practical overlap with continuation-passing style:

```haskell
type Codensity m a = forall b. (a -> m b) -> m b
```

Use codensity for bind-heavy structures only with semantic equivalence tests and benchmark evidence. Sources: `[KAN-HINZE-2012]`, `[KAN-MILEWSKI-2017]`.
