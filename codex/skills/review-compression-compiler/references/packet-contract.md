# Review Compression Packet Contract v2

The compact packet is mandatory for meaningful compiler use.

## Required literal key

```yaml
review_compression_packet:
```

Future audits may search for this exact string. Do not replace it with prose.

## Required statuses

```text
accepted | blocked | not-required
```

`not-required` is valid only for isolated, direct, no-new-surface cases.

## Invalid states

- `add-new-surface` with unpaid rent.
- `accepted` with missing proof matrix.
- `accepted` without implementation handoff.
- `same_cluster_findings >= 2` with `not-required`.
- Prose-only "normal form" with no packet.
