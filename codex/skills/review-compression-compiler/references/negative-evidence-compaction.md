# Negative Evidence Compaction

When the same exclusion family appears 3+ times, compact into a route-family exclusion:

```yaml
negative_compaction:
  compacted_card_id: "NREC-FAMILY-..."
  hypothesis_family:
  excluded_route_family:
  evidence_refs: []
  current_applicability:
  reopening_test:
  safest_next_frontier:
```

Compaction prevents the ledger from becoming noisy while preserving route-shaping evidence.
