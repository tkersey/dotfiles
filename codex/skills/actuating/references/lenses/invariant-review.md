# Invariant Review Lens

Independently inspect the exact bound subject for reachable illegal states,
owner ambiguity, transition gaps, identity drift, policy bypass, witness
mismatch, stale or duplicate effects, and generator/validator disagreement.

Every material finding must include:

```text
candidate predicate
state owner and scope
minimal counterexample trace
transition or boundary that permits it
current enforcement gap
falsifying proof signal
```

Reject decorative invariants, local assertions with no owner, and properties
with no current counterexample or proof obligation.

Return one structured `clean` or `findings` verdict. Do not launch the standalone
`$invariant-ace` authority fanout, select enforcement, implement, persist an
artifact, grant mutation, or certify closeout.
