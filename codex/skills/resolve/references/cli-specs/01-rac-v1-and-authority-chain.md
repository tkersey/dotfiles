# RAC-v1 And Authority Chain

`resolve-c3 authority-chain` validates a RAC-v1 artifact that transfers review
pressure into bounded mutation authority.

## Required Identity

- `rac_version`: `RAC-v1`
- `chain_id`
- `campaign_id`
- `review_claim_id`
- current artifact state for base/head or equivalent proof epoch

## Required Chain

A valid RAC-v1 links the review claim through:

```text
review claim -> AC-v2 horizon -> CEX/CEB -> MBK/RC -> proof obligation -> realization target
```

The gate fails closed when any link is missing, stale, unverifiable, outside the
accepted horizon, or not bound to current artifacts.

## Mutation Authority

`mutation_allowed` is true only when the authority chain is valid and the RAC
explicitly permits mutation for the requested claim. Non-mutation RAC artifacts
may be valid but must not authorize code changes.
