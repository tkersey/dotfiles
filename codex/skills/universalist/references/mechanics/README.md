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
Yoneda/Coyoneda representation
codensity and dense-dual presentations
defunctionalization
categorical data / CQL context compilation
pushout reconciliation
possibility sheafification mechanics
```

Use `pullback` when two source values or structures must agree through a shared observation. Use `pushout` when two sources must be glued along an explicit overlap. Use `double-pushout` for graph/model rewrites with delete-preserve-add structure and a potentially failing pushout complement.

Use `comonad-space` when locality is semantic and a world needs points with coherent neighborhoods. Use `density-comonad` when local patches should generate the spatial structure and a basis/reconstruction claim must be tested. Use `halo` for effective or labelled neighborhoods and germs. Use `continuous-comonad-map` when a boundary must preserve locality rather than only point values.

Do not conflate behavioral coalgebras with coalgebras of a comonad. The former model unfolding behavior; the latter model coherent situated/local structure.

The old `$kan` handoff is removed. Use `$universalist`; then read the relevant mechanics reference lazily.