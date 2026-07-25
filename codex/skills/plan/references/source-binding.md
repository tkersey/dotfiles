# Source Binding

A plan is synthesized against a specific intent and artifact state.

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

The recorded binding is provenance, not a claim that the state remains current.
At consumption time, an observed invalidator makes that binding stale. Plan may
declare invalidators; the consumer establishes whether they have fired.

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
