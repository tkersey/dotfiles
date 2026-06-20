---
name: review-adjudication
description: "Verify review claims against current code, classify branch liability and kernel impact, and route findings into kernel observation, witness attachment, validation, follow-up, rejection, or blocking. Under `$resolve`, never issue direct code-mutation authority."
metadata:
  version: "4.0.0"
---

# Review Adjudication

## Mission

Separate:

```text
observed fact
review claim
repair suggestion
branch liability
kernel impact
permitted disposition
```

## Required decision

```yaml
review_observation:
  observation_id:
  artifact_state:
  observed_behavior:
  required_behavior:
  validity:
    confirmed |
    refuted |
    stale |
    unknown
  liability:
    introduced_by_current_diff |
    exposed_and_required_by_current_acceptance |
    preexisting_but_blocks_current_invariant |
    adjacent_preexisting |
    reviewer_preference |
    unknown
  kernel_impact:
    existing_law_violation |
    additional_witness |
    missing_semantic_distinction |
    no_kernel_impact |
    unknown
  acceptance_entailment:
    entailed |
    scope_expansion |
    unknown
  reproduction_or_proof:
  source_refs: []
  disposition:
    enter_kernel |
    attach_witness |
    validate_only |
    capture_followup |
    reject |
    blocked
```

## Hard rules

- Valid does not mean branch-liable.
- Reviewer repair suggestions are not implementation scope.
- `additional_witness` does not create a new code branch or test family.
- `missing_semantic_distinction + scope_expansion` returns to spec/user authority.
- Under `$resolve`, emit no direct mutation warrant.
- Raw review prose must not be handed to an implementer.
