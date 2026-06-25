# Human Projection

The human plan is a compact explanation of EPG-v1.

Required headings:

```text
Strategy Summary
Source and Invariants
Current Belief and Critical Unknowns
Commitment Horizon
Policy Branches
Proof, Rollback, and Terminal States
Policy Delta
Execution Policy Graph
```

Rules:

- Reference stable IDs.
- Show the next commitment horizon explicitly.
- Show critical unknowns and the evidence/action that resolves each.
- Show branch conditions and terminal routes.
- Distinguish policy horizon from active commitment.
- Do not repeat every JSON field.
- Do not include internal iteration history.
- Do not claim readiness outside the derived EPG gate.
- `Execution Policy Graph` contains exactly one fenced JSON EPG object.
