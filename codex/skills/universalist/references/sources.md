# Sources and claim boundaries

Use sources only to support mathematical/programming claims. Architecture recommendations are engineering interpretations unless the repo explicitly models the relevant category, maps, universal property, and law.

Stable references:

- Mac Lane, *Categories for the Working Mathematician*: adjunctions, products/coproducts, limits/colimits, pullbacks, pushouts, Yoneda, Kan extensions.
- Riehl, *Category Theory in Context*: modern presentation of universal properties, limits/colimits, pullbacks/pushouts, adjunctions, and Kan extensions.
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

## Codex workflow sources

- OpenAI Codex Subagents: https://developers.openai.com/codex/subagents
- OpenAI Codex Subagent concepts: https://developers.openai.com/codex/concepts/subagents
- OpenAI Codex Skills: https://developers.openai.com/codex/skills
