# Source Binding

A policy is compiled for a specific intent and artifact state.

Required when spec-governed:

```text
spec ID
SGR/governance ref
source refs and digest
locked decision refs
```

Required when repository-bound:

```text
repository
branch
base
head
dirty fingerprint
created-at timestamp
```

A policy becomes stale when any declared invalidator fires.

Common invalidators:

```text
spec/source digest changes
accepted decision superseded
repository head/tree changes materially
required API/protocol disappears
proof command/build topology changes
critical fact loses freshness
```

Stale handling is explicit:

```text
return_to_spec
return_to_grill
replan
refresh_authority
block
```

Never mutate a sealed source binding in place. Emit a new policy revision.
