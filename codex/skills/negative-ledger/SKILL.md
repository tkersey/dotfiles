---
name: negative-ledger
description: "Durably record falsified semantic routes in `.ledger/negative-ledger.jsonl`: failed realization designs, wrong authority models, overdistinguished kernels, local-surface families that failed to close a law, and proof-wound patterns. Use for `$negative-ledger`, kernel/realization route exclusion, reopening, compaction, or MBKC negative evidence."
metadata:
  version: "5.0.0"
---

# Negative Ledger

## Mission

Prune semantic search space, not merely exact patches.

Capture:

```text
failed realization route
wrong authority model
overdistinguished kernel
local-surface family that failed to close a governing law
proof-wound pattern
```

Canonical store:

```text
.ledger/negative-ledger.jsonl
```

## Record

```yaml
negative_evidence_record:
  record_version: NER-v2
  campaign_id:
  kind:
    realization_route |
    authority_model |
    kernel_distinction |
    proof_pattern
  kernel_law_ids: []
  counterexample_family_ids: []
  route_or_model_id:
  hypothesis:
  observed_outcome:
  falsifying_evidence: []
  exclusion_scope:
    exact |
    route_family |
    authority_model |
    distinction_pattern |
    proof_pattern
  exclusion_rule:
  reopening_criteria: []
  applicability:
  status:
    active |
    capture_candidate |
    reopened |
    stale |
    superseded |
    accepted_risk
```

## Rules

- Cluster identity alone is not exclusion.
- A new helper name does not create a new route.
- A local-surface fix that produces another witness of the same law is negative evidence against that semantic route.
- A kernel distinction with no accepted observation should be captured as overdistinction.
- One-test-per-wound recurrence should exclude that proof pattern.
- MBKC lists active, reopened, stale, and superseded evidence.
- Missing durable ledger during repeated semantic-route selection blocks terminal certification.
