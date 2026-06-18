# Review Governor Handoff v3

When invoked by `$resolve`, implement the selected permitted route—not the review queue.

Reject when:

- RGR-v3 is required but missing;
- RGR-V3-MUTATION-PERMIT is missing/stale;
- finding liability does not permit mutation;
- normal form is falsified and route is another ordinary normal form;
- fuse is tripped without passing distillation/deletion/boundary route;
- owner pressure exceeded but route continues the same owner;
- production-net gate rejects change kind;
- negative evidence excludes route or required capture is missing;
- route did not change leverage after falsification;
- proof matrix failed;
- scope/budget/forbidden actions are missing.

A permit is cumulative. Commits do not reset its counters.

Stop and return to `$resolve` when:

- budget is exhausted;
- actual change kind differs from permitted change kind;
- a new same-family finding appears;
- implementation needs a new owner/file/helper/branch not permitted;
- deletion offset cannot be delivered.

Emit:

```yaml
fixed_point_receipt:
  permit_id:
  selected_route:
  normal_form_id:
  fuse_state:
  actual_change_kind:
  actual_production_net:
  budget_exhausted: yes | no
  family_recurred: yes | no
  handoff_result: completed | return_to_governor | blocked
```
