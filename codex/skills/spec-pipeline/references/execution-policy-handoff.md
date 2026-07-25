# Handoff to `$plan`: Execution Policy Graph

`$spec-pipeline` owns accepted semantics and the architectonic decisions made by the
specification within that authority.

A ready handoff should provide:

```text
spec ID and SGR/governance receipt
source refs and digest
goal and binary terminal predicates
required and forbidden behavior
authority and compatibility boundaries
scope and non-goals
Architectonic Thread and seam authority
selected, evidence-conditioned, and downstream-open organizations
factor dispositions, laws, falsifiers, residuals, and invalidators
proof bar
locked user decisions
known facts and unresolved semantic questions
```

`$plan` compiles those semantics into EPG-v1. It does not require any implementation
or actuation workflow to do so.

It may add:

```text
plan-local architectonic seams
source-bounded architecture refinements
belief state and execution unknowns
observations and probes
guarded actions
execution owners/boundaries/lock roots
proof and rollback actions
policy branches
safety shield
progress potential
commitment horizon
architecture-policy transport squares
```

Authority law:

```text
source-fixed seam
  preserve or return to source authority

source-bounded seam
  refine only inside the declared observations, compatibility, scope,
  authority, and proof envelope

downstream-open seam
  select only from the declared admissible space using its decision observations
```

`$plan` may not silently change requirements, source-fixed architecture,
compatibility, authority, or proof bar. An architecture change inside a
source-bounded or downstream-open seam is a normal planning refinement when the
resulting architecture-policy square commutes.

A planning-discovered contradiction with source-fixed semantics returns to
`$spec-pipeline` and invalidates downstream policy/runtime artifacts. A plan-local or
source-bounded improvement revises the plan and restarts its existing fixed-point
synthesis from the earliest affected lens.
