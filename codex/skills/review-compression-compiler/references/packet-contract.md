# Packet Contract

Use `RCP-v1` for direct review compression and `RDP-v1` for review distillation.

A meaningful compiler use emits one of:

```yaml
review_compression_packet:
review_distillation_packet:
```

Required cross-cutting fields:

- `negative_evidence`
- `universalist_check`
- `selected_normal_form`
- `abstraction_rent`
- `proof_matrix`
- `implementation_handoff`
- `route_wave_ref`
- `closure_rule`

Invalid states:

- add-new-surface with unpaid rent.
- hot cluster with missing universalist check.
- repeated route failure with `negative_evidence.query_status: not-run`.
- accepted packet with no route-wave ref.
- distillation packet that permits cherry-picking lab commits as delivery.
