# Finding Liability

Concern validity and branch liability are separate.

```yaml
finding_liability:
  relation:
    introduced_by_current_diff |
    exposed_and_required_by_current_acceptance |
    preexisting_but_blocks_current_invariant |
    adjacent_preexisting |
    reviewer_preference |
    unknown
  mutation_allowed:
  disposition:
  evidence_refs:
  reason:
```

A valid adjacent preexisting defect should normally become a follow-up, not branch growth.

`address` is invalid without a mutation-capable liability.
