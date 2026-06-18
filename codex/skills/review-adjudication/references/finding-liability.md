# Finding Liability for Cleanroom Resolve

Review adjudication must separate:

```text
claim validity
branch liability
delivery recipe eligibility
```

Use:

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
    include_in_contract |
    validate_only |
    capture_followup |
    resolve_thread_only |
    reject |
    blocked
```

Only `include_in_contract` may feed CEC-v1.

A valid adjacent preexisting defect is a follow-up, not automatic delivery scope.
