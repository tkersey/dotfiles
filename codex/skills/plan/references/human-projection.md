# Human Projection

The human plan is a compact explanation of EPG-v1 and, in `spec-to-plan`, the
governed specification from which it was synthesized.

Required headings for `spec-to-plan`:

```text
Governed Specification
Plan Identity
Strategy and Source
Architecture and Abstraction
Belief, Unknowns, and Observations
Actions and Policy Branches
Proof, Rollback, and Terminals
Execution Policy Graph
```

`direct` or `revise` may omit `Governed Specification` only when the accepted source
or revision delta already exposes the same semantics without duplication.

Rules:

- Reference stable IDs.
- Show objective, scope, non-goals, locked decisions, requirements, proof bar,
  rollback, binary done-state, and open/deferred items in the governed view.
- Show consequential architectonic seams, authority, selected or conditioned
  organization, factor dispositions, law, falsifier, residuals, and invalidators.
- Show why the selected organization is not dominated by the ordinary candidate.
- Show which actions realize, migrate, preserve, or retire each factor.
- Show compatibility-square results when architecture change transported policy.
- Show critical unknowns and the evidence/action resolving each.
- Show branch conditions, commitment horizon, and terminal routes.
- Distinguish policy horizon from active commitment.
- Do not repeat every JSON field or expose iteration history.
- Do not emit a specification receipt, readiness gate, source packet, execution
  handoff, or Plan-owned runtime artifact.
- `Execution Policy Graph` contains exactly one fenced JSON EPG object.
- Report `Plan synthesized.` after synthesis and, after exact-byte validation,
  `EPG structurally valid under <definition-id>@<definition-digest>.`
- Never convert structural validity into semantic correctness, readiness, authority,
  or completion.

The governed specification and prose plan are on-demand projections from one source
model. EPG-v1 remains the sole authoritative planning artifact.
