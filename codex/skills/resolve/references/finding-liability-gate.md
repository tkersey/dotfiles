# Finding Liability Gate

A review finding may be true without belonging in the current branch.

Mutation-capable liabilities:

```text
introduced_by_current_diff
exposed_and_required_by_current_acceptance
preexisting_but_blocks_current_invariant
```

Non-mutation dispositions:

```text
adjacent_preexisting -> capture_followup
reviewer_preference -> reject or resolve_thread_only
unknown -> validate_only or blocked
```

Require proof when claiming a preexisting issue blocks the current invariant.
