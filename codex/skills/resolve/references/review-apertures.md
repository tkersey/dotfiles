# RAP-v1 — Review Aperture

A review aperture is a bounded falsification assignment.

```yaml
review_aperture:
  aperture_version: RAP-v1
  aperture_id:
  campaign_id:
  batch_id:
  review_mode:

  target:
    law_refs: []
    owner_refs: []
    operation_refs: []
    transition_refs: []
    proof_refs: []
    existing_class_refs: []

  requested_counterexample_kinds: []
  excluded_scope: []
  risk:
  overlap_with: []
  whole_diff_allowed:
  evidence_refs: []

  gate:
    target_nonempty:
    conformance_is_targeted:
    overlap_explained:
    aperture_allowed:
```

## Scheduling objective

Maximize:

```text
uncovered law coverage
novel counterexample probability
independent owner/transition coverage
```

Minimize:

```text
lane overlap
whole-diff rereading
duplicate findings
review cost
```

## Reviewer prompt

```text
Attempt to falsify the named laws at the named owners/transitions.
Return a minimal CEX-v1 trace or clean.
Do not conduct general feature discovery.
```
