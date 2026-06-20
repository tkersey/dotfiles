# Proof Mapping

## Proof surface

```yaml
proof_surface:
  proof_surface_id:
  law_or_invariant_ids: []
  kind:
  artifact_refs: []
  strength:
  gaps: []
```

Kinds:

```text
type/representation
constructor
static analysis
unit test
table test
property test
state-machine test
integration test
compile-fail
runtime witness
CI gate
review only
```

## Strength questions

- Does the proof target a law or one example?
- Is it current to the artifact state?
- Can a bad implementation still pass?
- Does it cover transitions and rollback?
- Is it deterministic?
- Is the proof duplicated?
- Is the only proof a reviewer remembering the rule?

## Proof debt

```text
law with no executable proof
one test per historical wound
duplicate fixture families
broad suite with no claim mapping
runtime-only check for structural invariant
stale/manual receipt
```

## Compression

Prefer a table, property, state machine, or generative family when several examples witness one law.
