# Implementation patterns

## Pattern: finite left Kan extension in `Set`

Use when the source and target categories are explicit and small.

Representation:

```text
LanValue(d) = quotient of {(c, u:Kc->d, x:Fc)} by source morphism action
```

Code shape:

- category data type with objects and arrows;
- functor data type mapping objects/arrows;
- union-find for quotient;
- `eta(c, x)` smart constructor;
- action on target arrows `g : d -> d'` sends class `(c,u,x)` to `(c,g∘u,x)`.

Law tests:

- quotient respects composition;
- unit naturality;
- factorization through a sample target functor `G`.

Sources: `[KAN-RIEHL-CTIC]`.

## Pattern: finite right Kan extension in `Set`

Representation:

```text
RanValue(d) = { coherent family x_(c,u) in Π_(u:d->Kc) F(c) }
```

Code shape:

- enumerate `d ↓ K`;
- generate product candidates or solve constraints;
- filter by compatibility equations;
- `epsilon(c, family)` projection at `id_Kc`;
- action on target arrows `g : d' -> d` sends a family over `d` to a family over `d'` by precomposition with `g`.

Law tests:

- family coherence;
- counit naturality;
- factorization from a sample source of observations.

Sources: `[KAN-RIEHL-CTIC]`.

## Pattern: coend/existential left Kan

Haskell-shaped form:

```haskell
data Lan k d a = forall i. Lan (k i -> a) (d i)
```

Engineering shape:

```text
package hidden_i with:
  project : K hidden_i -> a
  payload : D hidden_i
```

Use for generated target values from hidden source indices, syntax extension with a hidden core witness, and serialization/deserialization bridges.

Sources: `[KAN-MILEWSKI-2017]`, `[KAN-HASKELL-KAN-EXTENSIONS]`.

## Pattern: end/rank-n right Kan

Haskell-shaped form:

```haskell
newtype Ran k d a = Ran { runRan :: forall i. (a -> k i) -> d i }
```

Engineering shape:

```text
for every observation from a into K(i), produce a D(i), uniformly in i
```

Use for compatibility facades, continuation-like encodings, codensity/CPS optimization, and representing a value by all ways it can be observed.

Sources: `[KAN-MILEWSKI-2017]`, `[KAN-HINZE-2012]`.

## Pattern: codensity optimization

Shape:

```haskell
newtype Codensity m a = Codensity { runCodensity :: forall b. (a -> m b) -> m b }
```

Use when a monadic/free/interpreter structure is heavily left-associated, the bottleneck is allocation or repeated reassociation, and semantic observations are parametric enough to preserve meaning.

Tests:

- `lowerCodensity . liftCodensity` equals identity on representative programs;
- error ordering/resource behavior is unchanged;
- benchmark old/new workload.

Sources: `[KAN-HINZE-2012]`.

## Pattern: Yoneda/Coyoneda preprocessing

Yoneda-like forms avoid repeated mapping by deferring transformations. Coyoneda-like forms can make a non-functorial-looking structure mappable by packaging a source value with a projection.

Use as adjacent optimizations before reaching for full Kan-extension machinery.

Sources: `[KAN-MILEWSKI-2017]`, `[KAN-HASKELL-KAN-EXTENSIONS]`.

## Pattern: Kan lift

A Kan lift solves for a functor in a postcomposition situation rather than a precomposition situation. Use only when the unknown functor is naturally on the other side of composition. In architecture, this appears when deriving an internal representation so a fixed backend/output functor can reproduce an existing external behavior.

Guardrail: most software prompts that say “lift” only need ordinary adapter lifting, not a categorical Kan lift.

Sources: `[KAN-RIEHL-CTIC]`, `[KAN-MACLANE-CWM]`.
