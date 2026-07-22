# Sources and claim boundaries

Use sources only to support mathematical/programming claims. Architecture recommendations are engineering interpretations unless the repo explicitly models the relevant category, maps, universal property, and law.

Stable references:

- Mac Lane, *Categories for the Working Mathematician*: adjunctions, products/coproducts, limits/colimits, pullbacks, pushouts, density, Yoneda, Kan extensions, monads, and comonads.
- Riehl, *Category Theory in Context*: modern presentation of universal properties, limits/colimits, pullbacks/pushouts, adjunctions, density, and Kan extensions.
- Charles Ehresmann's work on categories structured internally in categories: foundational source of double categories.
- Marco Grandis and Robert Paré, “Limits in Double Categories,” *Cahiers de Topologie et Géométrie Différentielle Catégoriques* 40 (1999): double limits, tabulators/cotabulators, and two-dimensional universal properties.
- Michael Shulman, “Framed Bicategories and Monoidal Fibrations,” *Theory and Applications of Categories* 20 (2008); arXiv:0706.1286: pseudo double categories, framed bicategories/equipments, base change, companions, and conjoints for spans, bimodules, distributors, and related generalized morphisms.
- Thomas Fiore, Nicola Gambino, and Joachim Kock, “Monads in Double Categories,” *Journal of Pure and Applied Algebra* 215 (2011); arXiv:1006.0797, and “Double Adjunctions and Free Monads,” arXiv:1105.6206: formal category theory, double adjunctions, universal squares, free monads, and representability in double categories.
- Kenny Courser, “Open Systems: A Double Categorical Perspective,” arXiv:2008.02394: symmetric monoidal double categories of structured/decorated cospans and applications to open circuits, Markov processes, and Petri nets.
- Evan Patterson, “Structured and Decorated Cospans from the Viewpoint of Double Category Theory,” arXiv:2304.00447: double-categorical universal properties, equipments, and compositional open systems.
- Michael Lambert and Evan Patterson, “Representing Knowledge and Querying Data using Double-Functorial Semantics,” arXiv:2403.19884: unifying functions and relations through double functors and relational-query semantics.
- David Jaz Myers, “Double Categories of Open Dynamical Systems,” arXiv:2005.05956: indexed double categories, open dynamical systems, covariant/contravariant morphisms, and compositional behavior.
- Sophie Libkind and David Jaz Myers, “Towards a Double Operadic Theory of Systems,” arXiv:2505.18329: systems as modules over symmetric monoidal double categories of interfaces and interactions.
- Brian Day, “On closed categories of functors,” *Reports of the Midwest Category Seminar IV*, LNM 137 (1970): original closed functor-category/Day convolution construction.
- Brian Day, “Promonoidal functor categories” (1977): convolution over promonoidal rather than necessarily representable monoidal composition kernels.
- Edmund Robinson and Joshua Wrigley, “Day algebras,” *Mathematical Structures in Computer Science* 36 (2026), e6; arXiv:2504.06200: Day extension of algebraic and partial algebraic operations, with residuation and logic applications.
- Ross Street and Craig Pastro, “Doubles for monoidal categories,” *Theory and Applications of Categories* 21 (2008); arXiv:0711.1859: Tambara modules, their free/cofree constructions, the double of a monoidal category, strong Tambara modules, Day convolution, and monoidal centers.
- Bryce Clarke, Derek Elkins, Jeremy Gibbons, Fosco Loregian, Bartosz Milewski, Emily Pillmore, and Mario Román, “Profunctor Optics: a Categorical Update,” *Compositionality* 6 (2024); arXiv:2001.07488: generalized/mixed Tambara modules, optic categories, residual coends, and the profunctor representation theorem.
- Matteo Capucci, “Seeing double through dependent optics,” arXiv:2204.10708: dependent Tambara modules via double-category actions and horizontal naturality.
- Mateusz Stroiński, “Module categories, internal bimodules and Tambara modules,” *Proceedings of the London Mathematical Society* 128 (2024); arXiv:2210.13443: Tambara modules as generalized morphisms between module categories, representability/right adjoints, reconstruction, Morita theory, and action via enrichment.
- Mitchell Riley, “Categories of Optics,” arXiv:1809.00738: lawful optics and the separation between optic representation/composition and domain optic laws.
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

Tambara-module results cited above are established categorical/programming-language results in their stated hypotheses. Treat mappings to middleware, tenant/evidence/capability framing, Exact Context, comonadic halos, repository architecture, and coding-agent workflows as engineering interpretations unless the code explicitly models the ambient action, profunctor, framing laws, and representation theorem assumptions.

Double categories, equipments, structured cospans, and double-functorial semantics are established categorical constructions in their stated hypotheses. Treat mappings to repository refactors, migration proof leases, software-change calculus, query transport, and architecture-evolution squares as engineering interpretations unless the code explicitly models both arrow families, squares, pasting, interchange/coherence, and effective interpretation.

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

For double-category claims, distinguish:

```text
literal strict/pseudo/virtual double category or equipment
effective repository-native realization of the arrow/square/pasting laws
two-dimensional diagram analogy only
```

Require:

```text
two semantically distinct arrow families
identities and composition in both directions
typed squares with four matching boundaries
horizontal and vertical square pasting
interchange or an explicit coherent comparison
interpreter/double-functor preservation
effective normalization, resource, and invalidation policy
```

Do not call two categories, a commutative square, a PROP diagram, or a DPO rewrite a double category by itself. Do not infer effect commutativity from interchange. Do not claim equipment structure without companions, conjoints, or restrictions and their laws.

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

For Tambara/contextual-morphism claims, distinguish:

```text
literal Pastro-Street/generalized Tambara module with ambient action and laws
effective software encoding of a context-stable profunctor or optic
framing analogy only
```

Require:

```text
ambient context category/world and tensor/unit or dependent/partial action
source and target actions
underlying profunctor/generalized capability
frame operation
unit, associativity, endpoint naturality, and context coherence
interpretation law
representability status
effective residual/context representation
```

Do not call a `Context<T>` wrapper, Reader parameter, dependency-injection container, middleware stack, or optic-shaped record a Tambara module. Do not infer effect commutativity, parallelism, resource duplication, or domain optic laws from framing. Do not call a generalized module representable without a concrete realizer/right-adjoint witness.

The term **Tambara** is overloaded. Always distinguish these profunctor/module-category Tambara modules from equivariant Tambara functors and Tambara-Yamagami categories.

## Codex workflow sources

- OpenAI Codex Subagents: https://developers.openai.com/codex/subagents
- OpenAI Codex Subagent concepts: https://developers.openai.com/codex/concepts/subagents
- OpenAI Codex Skills: https://developers.openai.com/codex/skills
