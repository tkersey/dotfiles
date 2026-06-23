# Simple Fixed-Point Frame: FPF-v1

Use outside `$actuating` only for bounded, unambiguous work.

```yaml
fixed_point_frame:
  frame_version: FPF-v1
  goal:
  canonical_owner:
  selected_route:
  permitted_scope: []
  forbidden_actions: []
  non_goals: []
  surface_budget:
  proof_obligations: []
```

Reject the mode when:

```text
more than one plausible owner
several materially different routes
behavioral quotient/equivalence decision
cross-workflow delivery authority
scope expected to expand
```

In those cases return `selection_required` to the owning workflow.
