# Review Compression Packet Contract v4

A meaningful compiler use emits a compact packet with literal key:

```yaml
review_compression_packet:
```

Required structural fields:

- `packet_version: RCP-v1`
- `selected_normal_form`
- `universalist_check`
- `falsification`
- `abstraction_rent`
- `proof_matrix`
- `implementation_handoff`
- `commit_boundary`
- `route_wave_ref`
- `closure_rule`

Invalid states:

- `add-new-surface` with unpaid rent.
- `add-new-surface` with `universalist_check.considered: no`.
- `accepted` with `universalist_check.decision: blocked`.
- prior `universalist not-needed` falsified but new decision remains `not-needed`.
- accepted packet without route-wave publication.
- prose-only normal form with no packet.
