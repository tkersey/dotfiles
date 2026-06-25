# Validation Matrix — VMX-v1

Use VMX for recurring or multidimensional semantic spaces.

Prefer equivalence classes to an exhaustive Cartesian product.

```yaml
validation_matrix:
  matrix_version: VMX-v1
  matrix_id:
  artifact_state:
  domain:
  owner:
  invariant:

  dimensions:
    - name:
      values: []

  equivalence_classes:
    - class_id:
      description:
      governing_invariant:
      representative_row:
      covered_combinations: []
      proof_obligation:

  rows:
    - row_id:
      class_id:
      conditions: {}
      expected:
        accept |
        reject |
        normalize |
        defer |
        error
      authority_owner:
      producer:
      validator:
      existing_proof_refs: []
      missing_proof: []
      status:
        open |
        selected |
        proved |
        reopened |
        superseded
      evidence_refs: []

  completeness:
    boundary_classes_covered: yes | no
    malformed_classes_covered: yes | no | not_applicable
    transition_classes_covered: yes | no | not_applicable
    known_unknowns: []

  gate:
    selected_rows_valid: yes | no
    duplicate_rows_absent: yes | no
    mutation_allowed: yes | no
```

## Trigger conditions

Use when:

- one green fix reveals an adjacent case;
- the same owner/invariant reopens;
- several fields jointly decide acceptance;
- formats or state transitions are versioned;
- parser/verifier or replay behavior is involved.

## Rules

- One row is one observable semantic case, not one implementation branch.
- Equivalent rows may share a proof obligation.
- Reopened rows preserve prior proof refs and state why they became insufficient.
- New rows update the frontier before another patch.
- Tests should cover families when possible, not create one wound-specific family per review comment.
