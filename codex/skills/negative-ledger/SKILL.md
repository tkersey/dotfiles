---
name: negative-ledger
description: "Durably capture, query, gate, reopen, compact, and hand off falsified route families and failed normal-form hypotheses from repo-local `.ledger/negative-ledger.jsonl`. Use for `$negative-ledger`, review lab route failures, same-family recurrence, normal-form falsification, route-family exclusion, delivery recipe exclusion, or cleanroom `$resolve` negative route memory."
metadata:
  version: "3.0.0"
---

# Negative Ledger

## Mission

Prevent the delivery compiler from reselecting failed route families.

```text
A failed lab route becomes durable search-space pruning.
```

Canonical store:

```text
.ledger/negative-ledger.jsonl
```

## Cleanroom role

In `$resolve`, the ledger records:

- lab routes tried;
- route families falsified;
- normal-form hypotheses falsified;
- route families excluded from the delivery recipe;
- reopened/stale/superseded exclusions.

The ledger is not just a preflight check. It is the review lab's memory.

## Preferred commands

```bash
ledger gate ...
ledger capture --json FILE
ledger query ...
ledger show --id NEG-...
ledger reopen --id NEG-...
ledger compact ...
ledger handoff
ledger audit
```

Compatibility:

```bash
ledger map --route "$ROUTE" --cluster "$CLUSTER" --artifact "$HEAD_SHA"
ledger capture --json FILE
ledger doctor
```

## Required record on route failure

```yaml
negative_evidence_record:
  record_version: NER-v1
  neg_id:
  lab_id:
  recipe_id:
  cluster_id:
  counterexample_family:
  route_id:
  route_family:
  normal_form_id:
  hypothesis:
  attempted_change_or_decision:
  observed_outcome:
  failure_class:
  source_refs: []
  exclusion_scope: route | route_family | counterexample_family | cluster_wide | none
  exclusion_rule:
  reopening_criteria: []
  status: active | capture_candidate | non_exclusion_observation | reopened | stale | superseded | accepted-risk | blocked
  delivery_recipe_effect:
    excluded_from_recipe: yes | no
    replacement_route_family:
```

## Hard rules

- Every falsified lab route gets a record or an explicit no-write justification.
- Same-family recurrence after a route requires capture.
- Cluster-only evidence is related evidence, not automatic exclusion.
- Fuzzy matches are suggest-only.
- Delivery recipe cannot use an active excluded route family.
- If ledger is unavailable during a repeated route decision, `$resolve` must fail closed or use a scratch negative record and mark closure blocked until durable capture succeeds.
