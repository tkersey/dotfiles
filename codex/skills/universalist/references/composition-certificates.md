# Composition Certificates

A Composition Certificate is the reviewable unit of Universal Composition Doctrine. It documents one meaningful cross-world boundary and the canonical artifact that owns its composition.

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
  Location: after boundary / behind boundary / inside syntax / inside behavior / inside effects / inside observation / inside generation / inside callback/control flow

Canonical artifact
  Artifact:
  Why this artifact:
  Nearby alternative rejected:

## Composition grammar

Geometry: category / monoidal / Freyd-premonoidal / operad / PROP-properad / traced-coalgebraic / resource-sensitive
Colors / port types:
Primitive operations / components:
Substitution / wiring rules:
Symmetry / ordering / centrality:
Multiple-output or feedback requirements:
Forbidden wiring / effect reorderings:
Semantic algebras / interpretations:

## Effect geometry

Pure world/category:
Effectful world/category:
Pure embedding `J`:
Central operations:
Evaluation order:
Context action / value threading:
Certified commuting or parallel operations:
Noncommuting witness:

Presentation
  Mode: algebraic / codensity / mixed / primitive
  Generators / operations / equations:
  Dense probes / finite approximants:
  Dualizing observation object:
  Reconstruction / codensity operation:
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
  Negative witness / falsifier:

Status
  planned / implemented / verified / obstructed / primitive exception
```

## Certification outcomes

- **Verified**: artifact, interpreter/projection, positive law, falsifier, and bypass policy are in place.
- **Obstructed**: a free/lifted/canonical artifact cannot exist yet; the missing evidence, structure, or template is named.
- **Primitive exception**: the boundary is intentionally treated as a primitive effect and is contained by handlers/observations.
- **Planned**: certificate exists but code/laws are not implemented.

## Review questions

1. What boundary does this artifact own?
2. What would bypass it?
3. What law proves the boundary?
4. What falsifier prevents wishful thinking?
5. Is this a canonical artifact or just a renamed adapter?


## Presentation review questions

1. Is the artifact presented algebraically, codensely, by a mixed strategy, or as a contained primitive?
2. If algebraic, are generators/equations/handlers explicit?
3. If codensity/dense-dual, what are the probes, dualizing object, reconstruction, and domain-specific assumption?
4. Does the presentation simplify the boundary or merely rename it?
