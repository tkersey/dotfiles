# Review Resolution Integration

Use `$negative-ledger` as the memory of falsified review-resolution decisions.

A repeated review decision is not just a repeated decision. It is a falsified hypothesis.

## Trigger during `$resolve` / `$review-compression-compiler`

Run negative-ledger query/map when:

- same cluster reappears after repair;
- selected normal form was falsified;
- `universalist_check.decision: not-needed` was falsified;
- add-surface route failed or became unsound;
- public bypass, compatibility path, fallback, parser tolerance, or proof matrix choice caused a CAS counterexample;
- Review Distillation Mode is active;
- one-change candidate resembles a prior failed route.

## Required packet fragment

```yaml
negative_evidence:
  query_status: not-run | no-applicable-negative-evidence | active | stale | reopened | blocked
  active_exclusions:
    - neg_id:
      excludes_route:
      exclusion_rule:
      reopening_criteria: []
  reopened_or_stale: []
  capture_required:
    - hypothesis:
      attempted_change_or_decision:
      observed_outcome:
      failure_class:
```

`query_status` cannot be `not-run` after same-cluster recurrence or falsified route.

## Closure rule

No selected normal form may violate active negative evidence unless the evidence is reopened, proven stale/superseded, or explicitly accepted by the user as a risk.
