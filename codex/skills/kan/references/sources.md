# Sources

Use this file to route source-backed claims. For machine-readable safe/unsafe boundaries, see `sources.yml`.

## Skill format

- `[OPENAI-CODEX-SKILLS]` OpenAI Developers, “Agent Skills – Codex.” Use for Codex skill shape, progressive disclosure, optional `scripts/`, `references/`, `assets/`, and `agents/openai.yaml`.
- `[OPENAI-API-SKILLS]` OpenAI Developers, “Skills | OpenAI API.” Use for API upload shape, zip upload, single top-level folder, hosted-shell mounting, and inline bundles.
- `[AGENT-SKILLS-SPEC]` Agent Skills open specification. Use for portable SKILL.md conventions.

## Kan foundations

- `[KAN-RIEHL-CTIC]` Emily Riehl, *Category Theory in Context*. Use for universal properties, `Lan_K ⊣ K* ⊣ Ran_K`, pointwise colimit/limit formulas, adjunction and representability context.
- `[KAN-MACLANE-CWM]` Saunders Mac Lane, *Categories for the Working Mathematician*. Use for classic background on Kan extensions, ends/coends, density/codensity, and adjunctions.

## Programming applications

- `[KAN-HINZE-2012]` Ralf Hinze, “Kan Extensions for Program Optimisation, Or: Art and Dan Explain an Old Trick.” Use for right Kan extensions, continuations, codensity monad, CPS, Church representations, and backtracking.
- `[KAN-MILEWSKI-2017]` Bartosz Milewski, “Kan Extensions.” Use for Haskell-shaped `Ran` and `Lan` witnesses and end/coend intuition.
- `[KAN-MILEWSKI-POINTWISE-2018]` Bartosz Milewski, “Pointwise Kan Extensions.” Use for pointwise intuition and explanatory translation analogies.
- `[KAN-HASKELL-KAN-EXTENSIONS]` Stackage/Hackage package page for `kan-extensions`. Use for library vocabulary and package existence, not formal proof claims.

## Data migration and databases

- `[KAN-SPIVAK-WISNESKY-FQL-2014]` David I. Spivak and Ryan Wisnesky, “A Functorial Query Language.” Use for schemas as categories and instances as functors.
- `[KAN-SCHULTZ-WISNESKY-AQL-2015]` Patrick Schultz and Ryan Wisnesky, “Algebraic Data Integration.” Use for `Σ_F ⊣ Δ_F ⊣ Π_F` functorial data migration framing.

## Advanced and adjacent

- `[KAN-PERRONE-THOLEN-2021]` Paolo Perrone and Walter Tholen, “Kan extensions are partial colimits.” Use for advanced theory of left Kan extensions as partial colimits.
- `[KAN-WEBER-2015]` Mark Weber, “Algebraic Kan extensions along morphisms of internal algebra classifiers.” Use for algebraic Kan extensions and exactness contexts.
- `[KAN-FRITZ-PERRONE-2018]` Tobias Fritz and Paolo Perrone, “A Criterion for Kan Extensions of Lax Monoidal Functors.” Use for lax monoidal Kan extension conditions.
- `[KAN-SHIEBLER-2022]` Dan Shiebler, “Kan Extensions in Data Science and Machine Learning.” Use for application-oriented examples, not primary definitions.
