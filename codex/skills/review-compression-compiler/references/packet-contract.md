# Review Compression Packet Contract

`review_compression_packet` is the authority-bearing artifact for cluster-level review compression.

## Required status

```yaml
packet_status: accepted | blocked | not-required
```

- `accepted`: selected normal form and implementation handoff are ready for `$fixed-point-driver`.
- `blocked`: missing evidence, stale artifact state, unpaid abstraction rent, unsafe proof gap, or unresolved owner.
- `not-required`: isolated item; local existing-owner route can proceed without compiler.

## Valid selected forms

```text
no-change-proof
validate-only
delete-collapse-canonicalize
refactor-existing-owner
mutate-existing-owner
add-new-surface
blocked
```

## Invalidation

A packet becomes stale when:

- `HEAD` changes;
- base/fingerprint changes for the reviewed artifact;
- new same-cluster counterexample appears;
- a proof surface changes;
- selected owner changes;
- implementation exceeds permitted scope or forbidden-action boundary.

## Integration rule

`$resolve` should not pass same-cluster production mutation to `$fixed-point-driver` unless it has an accepted packet or a structured not-required reason.
