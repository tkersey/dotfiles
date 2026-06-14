# Packet Contract

Use `RCP-v1` for direct review compression and `RDP-v1` for review distillation.

Use `NREC-v1` for negative route exclusions.

A meaningful compiler use emits one of:

```yaml
review_compression_packet:
review_distillation_packet:
```

A falsified or active-exclusion route emits or references:

```yaml
negative_route_exclusion_card:
```

Invalid states:

- add-new-surface with unpaid rent.
- hot cluster with missing universalist check.
- repeated route failure with `negative_evidence.query_status: not-run`.
- selected route matches active negative exclusion and is not reopened/stale/superseded.
- accepted packet with no route-wave ref.
- distillation packet that permits cherry-picking lab commits as delivery.
