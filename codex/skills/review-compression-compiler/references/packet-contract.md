# Review Compression Packet Contract v3

The compact packet is mandatory for meaningful compiler use.

## Required literal key

```yaml
review_compression_packet:
```

## Required structural fields

- `packet_version: RCP-v1`
- `selected_normal_form`
- `universalist_check`
- `abstraction_rent`
- `proof_matrix`
- `implementation_handoff`
- `commit_boundary`
- `closure_rule`

## Invalid states

- `add-new-surface` with unpaid rent.
- `add-new-surface` with `universalist_check.considered: no`.
- `accepted` with `universalist_check.decision: blocked`.
- same-cluster hot path with `not-required`.
- prose-only normal form with no packet.
