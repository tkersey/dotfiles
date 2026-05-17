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
