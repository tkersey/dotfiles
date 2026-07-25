# Human Projection

The human plan is a compact explanation of EPG-v1, including the architecture and
abstraction state over which the policy was synthesized.

Required headings:

```text
Strategy Summary
Source and Invariants
Architecture and Abstraction
Current Belief and Critical Unknowns
Commitment Horizon
Policy Branches
Proof, Rollback, and Terminal States
Policy Delta and Architectonic Transport
Execution Policy Graph
```

Rules:

- Reference stable IDs.
- Show consequential architectonic seams, their authority, selected or conditioned
  organization, factor dispositions, law, falsifier, residuals, and invalidators.
- Show the ordinary candidate and why the selected organization is not dominated.
- Show which actions realize, migrate, preserve, or retire each architectural factor.
- Show compatibility-square results when an architecture change transported policy.
- Show the next commitment horizon explicitly.
- Show critical unknowns and the evidence/action that resolves each.
- Show branch conditions and terminal routes.
- Distinguish policy horizon from active commitment.
- Make clear that accretive improvement may delete actions or abstractions while
  increasing justification and proof strength.
- Do not repeat every JSON field.
- Do not include internal iteration history.
- Report `Plan synthesized.` after synthesis. Report `Plan compiles.` only when a
  compatible compiler accepts the exact emitted EPG under its named structural
  contract.
- Compiler absence prevents only the compilation claim, not the Plan result.
- Do not emit a synthesis receipt, readiness gate, execution handoff, or Plan-owned
  runtime artifact.
- `Execution Policy Graph` contains exactly one fenced JSON EPG object.

The projection is generated on demand from the EPG. It is explanatory, not a second
authoritative artifact.
