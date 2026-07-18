# Mechanics references

These files are the former standalone `kan` skill folded into `universalist` as an internal mechanics layer.

Use these references only after `universalist` has identified:

```text
signal
seam/worlds
boundary kind
known side
unknown location
canonical artifact
witness slice
law/falsifier
certificate type
```

Mechanics include:

```text
Kan extensions and lifts
Freyd/AFT boundary diagnostics
Freyd categories / premonoidal effect geometry
Operads and typed composition grammars
Pullbacks, pushouts, and double-pushout graph rewriting
Comonads as spaces, density comonads, halos, and continuous locality-preserving maps
Day convolution, promonoidal convolution, and indexed-description composition
Tambara modules, mixed optics, contextual closure, and context-stable profunctors
Yoneda/Coyoneda representation
codensity and dense-dual presentations
defunctionalization
categorical data / CQL context compilation
pushout reconciliation
possibility sheafification mechanics
```

Use `pullback` when two source values or structures must agree through a shared observation. Use `pushout` when two sources must be glued along an explicit overlap. Use `double-pushout` for graph/model rewrites with delete-preserve-add structure and a potentially failing pushout complement.

Use `comonad-space` when locality is semantic and a world needs points with coherent neighborhoods. Use `density-comonad` when local patches should generate the spatial structure and a basis/reconstruction claim must be tested. Use `halo` for effective or labelled neighborhoods and germs. Use `continuous-comonad-map` when a boundary must preserve locality rather than only point values.

Use `day-convolution` when descriptions are indexed by a world with a tensor and every legal decomposition should contribute. Use `promonoidal-convolution` when composition is partial, relation-valued, or multi-witnessed. Use `applicative-convolution` for statically structured computation descriptions, `resource-convolution` for split/ownership assertions, and `spatial-convolution` for external-product patch systems.

Use `tambara-module` when a generalized transformation must remain valid under a shared context action. Use `mixed-optic` when source and target receive different actions, `free-tambara` when a bare capability must be closed under every legal frame, `dependent-tambara` when context changes indices, and `day-center-tambara` only when the closed/rigid hypotheses connecting strong Tambara modules to the Day center are explicit.

Do not conflate:

```text
pointwise product          same index only
Day convolution            all tensor decompositions
promonoidal convolution    partial/relational decompositions
operadic substitution      recursive typed insertion
monadic composition        value-dependent sequencing
Tambara framing            generalized morphism stable under context action
Freyd composition          ordered runtime effects
```

Do not conflate behavioral coalgebras with coalgebras of a comonad. The former model unfolding behavior; the latter model coherent situated/local structure.

Do not conflate these Tambara modules with equivariant Tambara functors. A `Context<T>` wrapper, reader parameter, or repeated middleware call is not a Tambara module without a real context action, profunctor, and framing laws.

The old `$kan` handoff is removed. Use `$universalist`; then read the relevant mechanics reference lazily.
