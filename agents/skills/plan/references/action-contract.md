# Action Contract

An action is a falsifiable bounded transition, not a task label. The same contract
applies to the human plan and optional EPG export.

Each consequential action names:

```text
stable ID and accountable owner
intended outcome and exact paths/symbols
prerequisite actions, required observations, and preserved invariants
bounded change and material effects
proof command or exact verifier reference, with artifact and branch binding
failure observation and safe successor, abort, or rollback route
```

Repository-affecting work needs nonempty paths and lock scope, including a probe
that edits benchmark or test code. Authority follows effects, not the action label.
Mutation, deployment, and stabilization need proof and actionable rollback or an
explicit pre-effect approval/abort boundary for irreversible work. An action must
predict an observable effect; failure without a modeled observation is incomplete.

A probe resolves or materially narrows a named unknown. A decision consumes named
evidence. A dependency names work that can actually precede it; reject unbootstrappable
prerequisite cycles. Every branch must admit a lawful successor or safe terminal,
including unavailable or inconclusive evidence when material.

## Construction and proof

For a consequential construction, bind:

```text
supported invalid family and assumptions
required-valid domain and compatibility
admission/ownership/transition/lifetime mechanism enforcing the law
independent source for sanctioned producers, consumers, and bypass coverage
preselected discriminator separating causal removal from example repair
verifier, artifact binding, claim strength, residuals, and falsifier
```

Choose the discriminator and coverage method before implementation. Do not derive
the proof universe solely from the candidate's asserted path list. A checked type's
name is not proof that every acquisition of trusted status crosses its boundary.
A smaller admitted domain is lawful only when required-valid behavior survives.
Samples and sibling tests are falsification evidence, not universal proofs; state
bounded claims honestly unless a justified construction or exhaustive domain proof
supports more. Plan chooses these obligations; execution proves the actual code.

Evidence closes an obligation only on a route that produces it. Shared obligations
with alternative implementations need branch-specific evidence or a common verifier
run after either route. Definition existence is not proof production.

## Machine encoding

Only for explicit export, use execution-policy-graph.md and epg-export.md. Preserve
EPG-v1 action kinds and wire fields. Utility cannot override safety or source
constraints; do not fabricate scoring machinery for the human plan. Repeatability
and retry routes must be explicit, not inferred from a failed action's remaining
eligibility.
