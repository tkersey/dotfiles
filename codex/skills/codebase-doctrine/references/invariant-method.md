# Owned Invariant Method

```yaml
owned_invariant:
  invariant_id:
  doctrine_status:
  normative_authority:
  statement:
  owner:
  source_of_truth:
  initialization:
  preserving_transitions: []
  violating_counterexamples: []
  enforcement_boundary:
  current_enforcement: []
  missing_or_late_enforcement: []
  exception_ownership:
  proof_surface_ids: []
  current_evidence_refs: []
  target_authority_refs: []
  gap_statement:
  evidence_refs: []
  confidence:
```

Begin with a bad trace:

```text
valid state -> transition -> invalid observable state
```

Reject or downgrade an invariant without owner, initialization, transition
coverage, violating counterexample, enforcement boundary, exception ownership,
and proof.

Prefer enforcement in this order when semantics permit:

```text
representation/type
constructor
canonical transition
transaction boundary
static tool
runtime validation
downstream tolerance
```
