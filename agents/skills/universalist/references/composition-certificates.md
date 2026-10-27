# Composition Certificates

A Composition Certificate is the reviewable unit of Universal Composition Doctrine. It documents one meaningful cross-world boundary, the canonical artifact that owns its composition, and—when relevant—the product used by descriptions indexed over that world.

## Template

```text
Worlds
  Source world:
  Target world:

Boundary
  Name:
  Kind:
  Function/module:
  Preserved:
  Forgotten:
  Generated:
  Observed:

Unknown
  Location: after boundary / behind boundary / local neighborhood / indexed descriptions / inside syntax / inside behavior / inside effects / inside observation / inside generation / inside callback/control flow

Canonical artifact
  Artifact:
  Why this artifact:
  Nearby alternative rejected:

Spatial geometry, when applicable
  Points:
  Local patches / subbasis:
  Basis / reconstruction:
  Effective halo / labels:
  Local/global identity:
  Restriction / germ:
  Continuous point/context transport:
  Resource / invalidation law:

Description composition, when applicable
  Index category/world:
  Tensor or promonoidal kernel:
  Unit:
  Indexed descriptions:
  Product: pointwise / Day / promonoidal / substitution / endofunctor composition
  Nearby product rejected:
  Legal decomposition witnesses:
  Coend/reindexing equivalence:
  Atomic/representable embedding:
  Executable representation:
  Enumeration / aggregation / normalization:
  Lax-monoidal interpreter:
  Residual/internal hom:
  Effect-order restrictions:
  Collision/provenance policy:
  Complexity/resource bound:

Composition grammar
  Geometry: category / monoidal / Freyd-premonoidal / operad / PROP-properad / traced-coalgebraic / resource-sensitive
  Colors / port types:
  Primitive operations / components:
  Substitution / wiring rules:
  Symmetry / ordering / centrality:
  Multiple-output or feedback requirements:
  Forbidden wiring / effect reorderings:
  Semantic algebras / interpretations:

Effect geometry
  Pure world/category:
  Effectful world/category:
  Pure embedding J:
  Central operations:
  Evaluation order:
  Context action / value threading:
  Certified commuting or parallel operations:
  Noncommuting witness:

Presentation
  Mode: algebraic / codensity / density-comonadic-spatial / mixed / primitive
  Generators / operations / equations:
  Dense probes / finite approximants:
  Dualizing observation object:
  Local patches / effective basis:
  Reconstruction / codensity operation:
  Restriction / continuity operation:
  Domain-specific theorem or assumption:
  Presentation law:
  Presentation falsifier:

Primitive effects
  Allowed primitives:
  Where they enter:
  Why they are contained:

Interpreter / projection / lowering / handler
  Function:
  Owner module:
  Bypass prevention:

Law witness
  Positive law test:
  Day representable/unit/associativity, if used:
  Decomposition soundness/completeness, if used:
  Quotient/interpretation law, if used:
  Negative witness / falsifier:

Status
  planned / implemented / verified / approximated / obstructed / primitive exception
```

## Certification outcomes

- **Verified**: artifact, interpreter/projection, positive law, falsifier, bypass policy, and any selected spatial/description mechanics are in place.
- **Approximated**: the effective implementation intentionally bounds locality, decomposition, quotient, or reconstruction and records the omitted cases and resource law.
- **Obstructed**: a free/lifted/canonical/spatial/convolutional artifact cannot exist yet; the missing evidence, structure, decidable quotient, finite support, or template is named.
- **Primitive exception**: the boundary is intentionally treated as a primitive effect and is contained by handlers/observations.
- **Planned**: certificate exists but code/laws are not implemented.

## Review questions

1. What boundary does this artifact own?
2. What would bypass it?
3. What law proves the boundary?
4. What falsifier prevents wishful thinking?
5. Is this a canonical artifact or just a renamed adapter?
6. If indexed descriptions compose, what index world and product make that composition lawful?
7. Is Day/promonoidal mechanics necessary, or would pointwise product, substitution, monadic sequencing, pullback, pushout, or an ordinary product be smaller?
8. Can decompositions and quotient normalization be implemented within the resource model?

## Presentation review questions

1. Is the artifact presented algebraically, codensely, spatially, by a mixed strategy, or as a contained primitive?
2. If algebraic, are generators/equations/handlers explicit?
3. If codensity/dense-dual, what are the probes, dualizing object, reconstruction, and domain-specific assumption?
4. If spatial, what are the patches, basis/halo representation, restriction, and continuity law?
5. Does the presentation simplify the boundary or merely rename it?
6. Remember that Day convolution is a description product, not a presentation mode.

## Day/promonoidal review questions

1. What are `C`, `tensor`, and `I`, or the promonoidal kernel `P(a,b;c)`?
2. What do `F(a)` and `G(b)` mean in code?
3. Which decompositions are legal and how are they enumerated or queried?
4. Which intermediate presentations are identified by the coend/normal form?
5. What information remains outside the quotient for provenance, ownership, effect order, or local identity?
6. Does `represent(a) star represent(b)` agree with `represent(a tensor b)`?
7. Does interpretation preserve convolution?
8. What prevents static/applicative structure from being mistaken for effect commutativity?
9. What collision, omitted decomposition, or operational explosion falsifies the design?
