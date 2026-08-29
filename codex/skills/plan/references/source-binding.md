# Source Binding

A plan is synthesized against a specific objective, governed source model, and
artifact state.

Required for `spec-to-plan`:

```text
governed specification identity or stable source refs
candidate and authoritative source digests
locked decision refs
scope and non-goals
proof and compatibility authority
```

Required for `direct`:

```text
direct accepted objective
source refs and digest
explicit direct-mode authority
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

The recorded binding is provenance, not a claim that state remains current. At
consumption time, an observed invalidator makes it stale. Plan may declare
invalidators; the consumer establishes whether they fired.

Common invalidators:

```text
source or governed-specification digest changes
accepted decision is superseded
repository head or tree changes materially
required API or protocol disappears
proof command or build topology changes
critical fact loses freshness
```

Stale handling is explicit:

```text
restart specification in a Plan revision
return to user judgment
replan
refresh authority
block
```

`return_to_spec` in EPG-v1 means a future Plan revision must restart the internal
specification phase. It is not a handoff to a separate skill.

Never mutate a sealed source binding in place. Emit a new policy revision.
