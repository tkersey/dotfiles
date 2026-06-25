# Handoff to `$plan`: Execution Policy Graph

`$spec-pipeline` owns accepted semantics.

A ready handoff should provide:

```text
spec ID and SGR/governance receipt
source refs and digest
goal and binary terminal predicates
required and forbidden behavior
authority and compatibility boundaries
scope and non-goals
architecture/design decisions
proof bar
locked user decisions
known facts and unresolved semantic questions
```

`$plan` compiles those semantics into EPG-v1.

It may add:

```text
belief state and execution unknowns
observations and probes
guarded actions
execution owners/boundaries/lock roots
proof and rollback actions
policy branches
safety shield
progress potential
commitment horizon
```

It may not silently change requirements, architecture, compatibility, authority, or proof bar.

A planning-discovered semantic contradiction returns to `$spec-pipeline` and invalidates downstream policy/runtime artifacts.
