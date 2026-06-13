# Proof Matrix

Do not add one test per wound unless that is truly the smallest proof.

## Matrix shape

```yaml
proof_matrix:
  - proof_id:
    counterexamples_covered: []
    command_or_test:
    existing_or_new: existing | new | modified | manual
    production_behavior_covered:
    fixture_risk: low | medium | high | unknown
    duplicate_test_risk: low | medium | high | unknown
```

## Minimize

Prefer proof that covers the family:

- invariant test;
- authority-boundary test;
- state-transition table;
- round-trip/canonicalization test;
- rejection matrix;
- one representative regression plus property-like table;
- existing test extension over new duplicate cases.

## Reject

- tests that admit impossible fixture states;
- broad snapshots that do not target the selected counterexamples;
- duplicate tests that differ only in incidental values;
- green commands unrelated to the selected normal form.
