# Mutation Gate

`resolve-c3 mutation-gate --chain RAC --review-claim-id ID --format json`
decides whether review-originated mutation may proceed.

## Inputs

- RAC-v1 artifact path
- review claim id
- current artifact state or proof epoch, when available

## Passing Conditions

The gate passes only when:

- the RAC-v1 artifact is valid;
- the requested review claim id is present in the RAC;
- the RAC is current for the working artifact state;
- `mutation_allowed` is true for the claim;
- the realization target is bounded by the accepted kernel/RC.

## Failure Semantics

Missing RAC, invalid RAC, stale artifact state, unknown review claim id, and
non-mutation RAC artifacts all fail closed. The output must preserve whether the
blocker is a projection limitation, invalid chain, stale state, or explicit
non-mutation decision.
