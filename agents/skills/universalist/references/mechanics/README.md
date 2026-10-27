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
Double categories, equipments, compatibility squares, pasting, and interchange
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

Use `double-categories.md` when two semantically different arrow families both compose and typed squares must paste horizontally and vertically with interchange/coherence. Use the equipment section only when strict maps induce effective companions, conjoints, or restrictions. One commuting square or DPO rewrite is not a double category.

Use `pullback` for agreement through a shared observation, `pushout` for gluing along explicit overlap, and `double-pushout` for delete-preserve-add graph/model rewriting.

Use comonadic mechanics when locality is semantic, Day/promonoidal mechanics when indexed descriptions compose through decompositions, and Tambara mechanics when a generalized transformation must survive context action.

Do not conflate:

```text
pointwise product          same index only
Day convolution            all tensor decompositions
promonoidal convolution    partial/relational decompositions
operadic substitution      recursive typed insertion
monadic composition        value-dependent sequencing
Tambara framing            generalized morphism stable under context action
double-category square     compatibility between two compositional arrow directions
Freyd composition          ordered runtime effects
```

Do not conflate a double category with a 2-category, PROP diagram, square fixture, or double-pushout rewrite. Require two arrow families, square typing, both pastings, interchange/coherence, and effective interpretation.

Do not conflate behavioral coalgebras with comonad coalgebras or profunctor Tambara modules with equivariant Tambara functors.

The old `$kan` handoff is removed. Use `$universalist`; then read the relevant mechanics reference lazily.
