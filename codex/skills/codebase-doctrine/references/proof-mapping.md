# Proof Mapping

```yaml
proof_surface:
  proof_surface_id:
  law_or_invariant_ids: []
  kind:
  artifact_refs: []
  strength:
  gaps: []
  evidence_refs: []
  verification:
    status: design_only | executed_current | historical | manual
    command:
    exit_code:
    result_ref:
    artifact_state_id:
    toolchain:
    target:
    options:
    verified_at:
    reason_not_executed:
```

`executed_current` requires a successful command bound to the current artifact
state.

A test path is not proof that the test currently passes.

Ask whether the proof targets a law or one example, covers transitions and
rollback, is deterministic, and can still pass a bad implementation.

Prefer a table, property, state machine, or generative family over one fixture per
historical wound.
