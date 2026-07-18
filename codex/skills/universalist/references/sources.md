# Sources and claim boundaries

Use sources only to support mathematical/programming claims. Architecture recommendations are engineering interpretations unless the repo explicitly models the relevant category, maps, universal property, and law.

Stable references:

- Mac Lane, *Categories for the Working Mathematician*: adjunctions, products/coproducts, limits/colimits, pullbacks, pushouts, density, Yoneda, Kan extensions, monads, and comonads.
- Riehl, *Category Theory in Context*: modern presentation of universal properties, limits/colimits, pullbacks/pushouts, adjunctions, density, and Kan extensions.
- Brian Day, “On closed categories of functors,” *Reports of the Midwest Category Seminar IV*, LNM 137 (1970): original closed functor-category/Day convolution construction.
- Brian Day, “Promonoidal functor categories” (1977): convolution over promonoidal rather than necessarily representable monoidal composition kernels.
- Edmund Robinson and Joshua Wrigley, “Day algebras,” *Mathematical Structures in Computer Science* 36 (2026), e6; arXiv:2504.06200: Day extension of algebraic and partial algebraic operations, with residuation and logic applications.
- McBride and Paterson, “Applicative Programming with Effects”: applicative functors as static effectful computation structure.
- Capriotti and Kaposi, “Free Applicative Functors”: free applicatives for analyzable embedded descriptions.
- Rivas and Jaskelioff, “Notions of Computation as Monoids”: monads, applicatives, and arrows as monoids in different monoidal categories.
- Dongol, Hayes, and Struth, “Convolution, Separation and Concurrency,” arXiv:1410.4235: convolution lifting for separation, interval, stream, and concurrency semantics.
- Lack and Sobociński, “Adhesive Categories”: well-behaved pushouts along monomorphisms, Van Kampen squares, and foundations for compositional graph rewriting.
- Ehrig et al., *Fundamentals of Algebraic Graph Transformation*: pushout complements, double-pushout rewriting, gluing conditions, typed graph and model transformation.
- Spivak/Wisnesky functorial data migration work: schemas as categories and Sigma/Delta/Pi migration.
- Schultz and Wisnesky, “Algebraic Data Integration”: CQL, schema/instance colimits, pushout integration, constraints, and provenance-aware migration.
- Fong and Spivak, *An Invitation to Applied Category Theory* / *Seven Sketches in Compositionality*: universal constructions, compositional systems, wiring diagrams, and applied categorical modeling.
- Reynolds, “Definitional Interpreters for Higher-Order Programming Languages”: origin context for defunctionalization.
- Danvy and Nielsen, “Defunctionalization at Work”: higher-order to first-order transformation.
- Power and Robinson, “Premonoidal Categories and Notions of Computation”: ordered effectful composition and central morphisms.
- Power and Thielecke, “Closed Freyd- and kappa-categories”: Freyd-category semantics for call-by-value.
- Spivak, “The Operad of Wiring Diagrams”: typed hierarchical system assembly.
- Garner, “Ionads”: generalized spaces as finite-limit-preserving comonads on indexed sets, bases, and continuous maps.
- Ahman and Uustalu, work identifying categories with polynomial comonads on `Set`: categorical examples of comonads as spaces.
- Fairbanks, Carlson, and Spivak, “Comonads as Spaces,” arXiv:2607.15091v1 (2026): density comonads as generalized subbases, bases via density in coalgebra categories, continuous maps distinct from ordinary comonad maps, underlying topological/category shadows, halos as formal infinitesimal neighborhoods, and Day convolution of suitable small comonads.

## Current-preprint boundary

“Comonads as Spaces” is a July 2026 v1 preprint. Treat its stated theorems as mathematical research claims from that version. Treat all mappings to codebase locality, dependency neighborhoods, Exact Context germs, impact analysis, and Universalist certificates as research-informed architecture inference—not established software-engineering consensus.

“Day algebras” was published in 2026 and generalizes Day extension to algebraic and partial operations. Treat Universalist mappings to software architecture selectors, context residuals, and agent workflows as engineering interpretation unless the code explicitly realizes the relevant functor category, kernel, and laws.

Mark every nontrivial claim as one of:

- mathematical;
- programming;
- architecture inference;
- repo observation.

For pullback/pushout claims, distinguish:

```text
formal universal property
software approximation of factorization/uniqueness
engineering analogy only
```

Do not call a join a pullback without a shared target and agreement equation. Do not call a merge a pushout without an explicit overlap object and maps into both sources. Do not call a textual or version-control rewrite a double-pushout rewrite unless the host category, rule span, match, pushout complement, and rewrite laws are modeled.

For comonadic spatiality claims, distinguish:

```text
literal comonad / coalgebra / density / continuity structure
effective software approximation of halos, bases, germs, and locality preservation
spatial metaphor only
```

Do not call a contextual wrapper a comonad without counit/comultiplication laws. Do not call example coverage a basis without canonical reconstruction/density evidence. Do not call a point-preserving boundary continuous without halo/restriction/label preservation. Do not collapse local points into global points without an explicit identification and provenance policy.

For Day/promonoidal convolution claims, distinguish:

```text
literal left Kan extension / coend in a functor or presheaf category
effective software realization of the same decomposition and quotient laws
convolution-inspired aggregation only
```

Do not call a pointwise product Day convolution. Do not call operadic substitution, monadic sequencing, schema merging, or numerical kernel code Day convolution without the appropriate index world and universal construction. Require a tensor or promonoidal kernel, unit, legal-decomposition witnesses, coend/normalization policy, representable law, interpretation law, and effective resource bound.

## Codex workflow sources

- OpenAI Codex Subagents: https://developers.openai.com/codex/subagents
- OpenAI Codex Subagent concepts: https://developers.openai.com/codex/concepts/subagents
- OpenAI Codex Skills: https://developers.openai.com/codex/skills
