# Behavioral Model

Use the smallest vocabulary that explains correctness:

```yaml
behavioral_model:
  carriers: []
  operations: []
  observations: []
  state_classes: []
  transitions: []
  laws: []
  non_laws: []
  forbidden_states_or_transitions: []
  interpreters_or_projections: []
  evidence_refs: []
```

A law requires status, normative authority, owner, observations,
counterexamples, evidence, proof obligations, and proof surfaces.

Record deliberate non-laws so current implementation accidents do not become
future doctrine.

Use state-machine language when algebraic vocabulary does not clarify the
domain.
