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

`$plan` synthesizes those semantics into EPG-v1 and validates the result through
its passive Ledger definition. It does not require an implementation or actuation
workflow to do so.

The handoff crosses as one PSC-v1 JSON object containing the exact final SGR-v2.
Before the tail-call, Spec Pipeline validates those objects under
`spec-pipeline/spec-governance-receipt` and
`spec-pipeline/plan-source-contract`. These structural passes do not decide whether
the handoff is semantically authorized.

It may add:

```text
explicitly delegated plan-local architectonic refinements
source-bounded architecture refinements
belief state and execution unknowns
observations and probes
guarded actions
action owners and bounded paths/symbols/lock roots
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
`$spec-pipeline` and invalidates the affected EPG and any consumer state derived
from it. A plan-local or source-bounded improvement revises the policy and restarts
its fixed-point synthesis from the earliest affected lens.
