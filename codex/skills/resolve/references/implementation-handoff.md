# Implementation Handoff

Implementation handoff after stop rule must include:

```yaml
implementation_handoff:
  target_skill:
  selected_route:
  owner:
  permitted_scope: []
  forbidden_actions: []
  proof_required: []
  negative_route_gate:
  surface_delta_budget:
```

Do not hand off if the stop rule is open or the selected route violates active negative evidence.
