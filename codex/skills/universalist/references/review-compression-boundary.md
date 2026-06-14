# Review Compression Boundary

`$review-compression-compiler` calls `$universalist` when a hot review cluster suggests the shape of truth may be wrong.

Use `$universalist` to answer:

```text
Is this still an existing-owner repair,
or is a boundary artifact / protocol / state-machine / explicit IR / context certificate / canonical projection missing?
```

Return or inform a boundary packet:

```yaml
universal_boundary_packet:
  packet_version: UBP-v1
  artifact_state_id:
  cluster_id:
  boundary_smell:
  candidate_boundary_artifact:
    kind: protocol | state-machine | context-certificate | explicit-ir | effect-signature | canonical-projection | none
    owner:
    seam:
  decision: climb | not-needed | blocked
  reason:
  proof_signal: []
```

If a prior `universalist_check.decision: not-needed` was falsified by a same-cluster recurrence, the boundary packet must explicitly explain why a boundary artifact remains unnecessary or select `climb` / `blocked`.

Do not implement here unless explicitly routed by a separate implementation workflow.
