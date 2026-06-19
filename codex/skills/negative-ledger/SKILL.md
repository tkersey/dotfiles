---
name: negative-ledger
description: "Durably preserve falsified repair routes and normal-form hypotheses in repo-local `.ledger/negative-ledger.jsonl`, then prune those route families from C³ candidate tournaments. Use for `$negative-ledger`, failed candidates, same-family recurrence, route exclusion, reopening, compaction, or delivery-candidate negative-route status."
metadata:
  version: "4.0.0"
---

# Negative Ledger

## Mission

Convert failed candidate routes into durable search-space pruning.

```text
failed candidate
-> evidence-backed route-family record
-> future tournament exclusion
```

Canonical store:

```text
.ledger/negative-ledger.jsonl
```

## C³ contract

Every candidate carries:

```yaml
negative_route:
  status: allowed | active_exclusion | reopened | stale | superseded | unknown
  refs: []
```

An active exclusion invalidates the candidate.

A failed candidate should capture:

```yaml
negative_evidence_record:
  record_version: NER-v1
  run_id:
  candidate_id:
  cluster_id:
  counterexample_family:
  route_family:
  hypothesis:
  attempted_change_or_decision:
  observed_outcome:
  failure_class:
  source_refs: []
  exclusion_scope: route | route_family | counterexample_family | cluster_wide | none
  exclusion_rule:
  reopening_criteria: []
  status: active | capture_candidate | non_exclusion_observation | reopened | stale | superseded | accepted-risk | blocked
  tournament_effect:
    excluded: yes | no
    replacement_route_family:
```

## Rules

- Cluster identity alone does not hard-exclude a route.
- Fuzzy matches are suggest-only.
- Same-family recurrence after a selected route requires capture.
- A new helper name does not establish a different route family.
- An unavailable ledger during repeated-route selection blocks final certification.
- `no active exclusion` must identify records considered and applicability.
- MRPC must list excluded, reopened, stale, and superseded route refs.
