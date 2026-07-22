# Sources and claim boundaries

Use sources only to support mathematical/programming claims. Architecture recommendations are engineering interpretations unless the repo explicitly models the relevant category, maps, universal property, and law.

Stable references:

- Mac Lane, *Categories for the Working Mathematician*: adjunctions, products/coproducts, limits/colimits, pullbacks, pushouts, density, Yoneda, Kan extensions, monads, and comonads.
- Riehl, *Category Theory in Context*: modern presentation of universal properties, limits/colimits, pullbacks/pushouts, adjunctions, density, and Kan extensions.
- Charles Ehresmann's work on categories internal to categories: foundational source of double categories.
- Marco Grandis and Robert Paré, “Limits in Double Categories,” *Cahiers de Topologie et Géométrie Différentielle Catégoriques* 40 (1999): double limits, tabulators/cotabulators, and two-dimensional universal properties.
- Michael Shulman, “Framed Bicategories and Monoidal Fibrations,” *Theory and Applications of Categories* 20 (2008); arXiv:0706.1286: pseudo double categories, framed bicategories/equipments, companions, conjoints, restrictions, and base change.
- Thomas Fiore, Nicola Gambino, and Joachim Kock, “Monads in Double Categories,” *Journal of Pure and Applied Algebra* 215 (2011); arXiv:1006.0797, and “Double Adjunctions and Free Monads,” arXiv:1105.6206: formal category theory, double adjunctions, universal squares, and free monads.
- Kenny Courser, “Open Systems: A Double Categorical Perspective,” arXiv:2008.02394: symmetric monoidal double categories of structured/decorated cospans and applications to open circuits, Markov processes, and Petri nets.
- Evan Patterson, “Structured and Decorated Cospans from the Viewpoint of Double Category Theory,” arXiv:2304.00447: equipments and compositional open systems.
- Michael Lambert and Evan Patterson, “Representing Knowledge and Querying Data using Double-Functorial Semantics,” arXiv:2403.19884: functions, relations, double functors, and relational-query semantics.
- David Jaz Myers, “Double Categories of Open Dynamical Systems,” arXiv:2005.05956: indexed double categories and compositional dynamical systems.
- Sophie Libkind and David Jaz Myers, “Towards a Double Operadic Theory of Systems,” arXiv:2505.18329: systems as modules over symmetric monoidal double categories of interfaces and interactions.
- Brian Day, “On closed categories of functors,” *Reports of the Midwest Category Seminar IV*, LNM 137 (1970): original Day convolution.
- Brian Day, “Promonoidal functor categories” (1977): convolution over promonoidal kernels.
- Edmund Robinson and Joshua Wrigley, “Day algebras,” *Mathematical Structures in Computer Science* 36 (2026), e6; arXiv:2504.06200.
- McBride and Paterson, “Applicative Programming with Effects.”
- Capriotti and Kaposi, “Free Applicative Functors.”
- Rivas and Jaskelioff, “Notions of Computation as Monoids.”
- Dongol, Hayes, and Struth, “Convolution, Separation and Concurrency,” arXiv:1410.4235.
- Lack and Sobociński, “Adhesive Categories.”
- Ehrig et al., *Fundamentals of Algebraic Graph Transformation*.
- Spivak/Wisnesky functorial data migration work and Schultz/Wisnesky, “Algebraic Data Integration.”
- Fong and Spivak, *An Invitation to Applied Category Theory* / *Seven Sketches in Compositionality*.
- Reynolds, “Definitional Interpreters for Higher-Order Programming Languages.”
- Danvy and Nielsen, “Defunctionalization at Work.”
- Power and Robinson, “Premonoidal Categories and Notions of Computation.”
- Power and Thielecke, “Closed Freyd- and kappa-categories.”
- Spivak, “The Operad of Wiring Diagrams.”
- Garner, “Ionads.”
- Ahman and Uustalu on categories as polynomial comonads on `Set`.
- Fairbanks, Carlson, and Spivak, “Comonads as Spaces,” arXiv:2607.15091v1 (2026).
- Ross Street and Craig Pastro, “Doubles for monoidal categories,” *Theory and Applications of Categories* 21 (2008); arXiv:0711.1859.
- Clarke et al., “Profunctor Optics: a Categorical Update,” *Compositionality* 6 (2024); arXiv:2001.07488.
- Matteo Capucci, “Seeing double through dependent optics,” arXiv:2204.10708.
- Mateusz Stroiński, “Module categories, internal bimodules and Tambara modules,” *Proceedings of the London Mathematical Society* 128 (2024); arXiv:2210.13443.
- Mitchell Riley, “Categories of Optics,” arXiv:1809.00738.

## Current-preprint boundary

“Comonads as Spaces” is a July 2026 v1 preprint. Treat its stated theorems as mathematical research claims from that version. Treat mappings to codebase locality, dependency neighborhoods, Exact Context germs, impact analysis, and Universalist certificates as research-informed architecture inference.

“Day algebras” was published in 2026 and generalizes Day extension to algebraic and partial operations. Treat Universalist mappings to software architecture selectors, context residuals, and agent workflows as engineering interpretation unless the code explicitly realizes the relevant functor category, kernel, and laws.

Tambara-module results are established categorical/programming-language results under their stated hypotheses. Treat mappings to middleware, tenant/evidence/capability framing, Exact Context, comonadic halos, repository architecture, and coding-agent workflows as engineering interpretations unless the code models the ambient action, profunctor, framing laws, and representation assumptions.

Double categories, equipments, structured cospans, and double-functorial semantics are established categorical constructions under their stated hypotheses. Treat mappings to repository refactors, migration proof leases, software-change calculus, query transport, and architecture-evolution squares as engineering interpretations unless the code explicitly models both arrow families, squares, both pastings, interchange/coherence, and effective interpretation.

Mark every nontrivial claim as one of:

- mathematical;
- programming;
- architecture inference;
- repo observation.

For pullback/pushout claims distinguish formal universal property, software approximation, and analogy. Do not call a join a pullback or merge a pushout without their actual maps and factorization obligations.

For double-category claims distinguish:

```text
literal strict/pseudo/virtual double category or equipment
effective repository-native realization of arrow/square/pasting laws
two-dimensional diagram analogy only
```

Require two semantically distinct arrow families, identities and composition in both directions, typed squares, both pastings, interchange/coherence, double-functor preservation, and effective normalization/resources/invalidation. Do not call two categories, a commuting square, a PROP diagram, or DPO rewriting a double category. Do not infer effect commutativity from interchange. Do not claim equipment without companions, conjoints, or restrictions and their laws.

For comonadic spatiality claims distinguish literal structure, effective approximation, and metaphor. Require center/coherence, basis/halo evidence, restriction, continuity, and resources.

For Day/promonoidal convolution distinguish literal Kan/coend construction, effective realization, and convolution-inspired aggregation. Require tensor/kernel, unit, decompositions, quotient, representable and interpretation laws, and resources.

For Tambara/contextual-morphism claims distinguish literal Tambara structure, effective software encoding, and framing analogy. Require ambient and endpoint actions, profunctor, frame operation, unit/associativity/naturality/coherence, interpretation, representability status, and effective context representation.

The term **Tambara** is overloaded. Distinguish profunctor/module-category Tambara modules from equivariant Tambara functors and Tambara-Yamagami categories.

## Codex workflow sources

- OpenAI Codex Subagents: https://developers.openai.com/codex/subagents
- OpenAI Codex Subagent concepts: https://developers.openai.com/codex/concepts/subagents
- OpenAI Codex Skills: https://developers.openai.com/codex/skills
