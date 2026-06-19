---
name: review-adjudication
description: "Treat review comments and generated findings as claims, verify them against current code, classify branch liability, and choose address/validate/follow-up/reject/blocked dispositions. In C³ `$resolve`, emit counterexample candidates only; never issue direct delivery-mutation authority."
metadata:
  version: "3.0.0"
---

# Review Adjudication

## Mission

Separate:

```text
observed fact
review claim
repair proposal
branch liability
permitted disposition
```

## Output

```yaml
review_claim_decision:
  finding_id:
  artifact_state:
  observed_fact:
  claim:
  validity: confirmed | refuted | stale | unknown
  liability:
    introduced_by_current_diff |
    exposed_and_required_by_current_acceptance |
    preexisting_but_blocks_current_invariant |
    adjacent_preexisting |
    reviewer_preference |
    unknown
  disposition:
    counterexample |
    validate-only |
    follow-up |
    resolve-thread-only |
    reject |
    blocked
  counterexample:
    observed_behavior:
    required_behavior:
    reproduction_or_proof:
    suspected_owner:
    source_refs: []
```

## C³ boundary

When `$resolve` is active:

- `counterexample` feeds the basis;
- follow-up/reject/thread-only never enter delivery scope;
- reviewer repair proposals are hints;
- no direct mutation warrant is emitted;
- no implementation skill receives raw review prose.
