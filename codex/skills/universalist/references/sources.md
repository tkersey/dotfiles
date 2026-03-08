# Sources (annotated)

## Classical universal constructions
- Saunders Mac Lane, *Categories for the Working Mathematician*.
- Emily Riehl, *Category Theory in Context*.
- Steve Awodey, *Category Theory*.

Use these when the prompt wants the classical statement of a universal property, a proof sketch, or a standard construction such as limits, colimits, adjunctions, or representability.

## Higher, enriched, and indexed references
- Jacob Lurie, *Higher Topos Theory*.
- G. M. Kelly, *Basic Concepts of Enriched Category Theory*.
- Bart Jacobs, *Categorical Logic and Type Theory*.
- *Homotopy Type Theory: Univalent Foundations of Mathematics*.

Use these only when the user explicitly asks for higher-categorical coherence, enrichment, dependent type semantics, or fibrational structure.

## Computer science manifestations
- Algebraic effects and handlers: look for classic Moggi-style effect semantics plus modern handler literature when the codebase already models effects explicitly.
- Functorial data migration and Kan extensions: use for schema migration, query translation, or shape-changing data flow.
- Profunctor optics and coend-style encodings: use for lenses, prisms, traversals, or advanced representation theorems.

Keep these in the advanced tier unless the prompt is already theory-heavy or the codebase clearly uses these abstractions.

## Algebra-Driven Design
- https://algebradriven.design/
- https://sandymaguire.me/blog/algebra-driven-design/
- https://leanpub.com/algebra-driven-design
- https://www.lulu.com/shop/sandy-maguire-and-john-hughes/algebra-driven-design/hardcover/product-4j4rp4.html

Use ADD after identifying the main construction when the internal combination laws matter more than the outer shape.

## Law discovery and testing tools
- https://hackage.haskell.org/package/QuickSpec
- https://research.chalmers.se/en/publication/201765
- https://hackage.haskell.org/package/QuickCheck
- https://hackage.haskell.org/package/hedgehog
- https://pkg.go.dev/testing/quick
- https://fast-check.dev

Verify tool availability in the repo before recommending any of them. If the tool is absent, fall back to deterministic checks in the existing test runner.
