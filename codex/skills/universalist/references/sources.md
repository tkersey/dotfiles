# Sources (annotated)

## Classical universal constructions

- Saunders Mac Lane, *Categories for the Working Mathematician*
- Emily Riehl, *Category Theory in Context*
- Steve Awodey, *Category Theory*

Use these when the prompt wants the classical statement of a universal property,
a proof sketch, or the standard mathematical framing.

## Higher, enriched, and indexed references

- Jacob Lurie, *Higher Topos Theory*
- G. M. Kelly, *Basic Concepts of Enriched Category Theory*
- Bart Jacobs, *Categorical Logic and Type Theory*
- *Homotopy Type Theory: Univalent Foundations of Mathematics*

Keep these in reserve for prompts that explicitly ask for higher-categorical
coherence, dependent type semantics, enrichment, or indexed structure.

## Practical design and refactoring references

- Martin Fowler, *Refactoring*
- Eric Evans, *Domain-Driven Design*
- Vaughn Vernon, *Implementing Domain-Driven Design*

Use these when the question is less about formal statement and more about where a
new type, adapter, or seam should land in a real codebase.

## Algebra-Driven Design

- https://algebradriven.design/
- https://leanpub.com/algebra-driven-design
- https://sandymaguire.me/blog/algebra-driven-design/

Use ADD after the main construction is chosen, especially when combination laws,
normal forms, or homomorphisms matter inside the chosen shape.

## Law discovery and testing tools

- https://hackage.haskell.org/package/QuickSpec
- https://hackage.haskell.org/package/QuickCheck
- https://hackage.haskell.org/package/hedgehog
- https://pkg.go.dev/testing/quick
- https://fast-check.dev

Verify tool availability in the repo before recommending any of them. If the
tool is absent, fall back to deterministic checks in the existing test runner.
