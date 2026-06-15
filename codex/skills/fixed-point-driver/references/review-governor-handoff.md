# Review Governor Handoff

When invoked by `$resolve`, `$fixed-point-driver` must implement the selected governor route, not the review finding queue.

Reject handoff when:

- review_governor_record is required but missing;
- selected route is local patching after same-cluster recurrence without normal-form justification;
- active negative evidence excludes the selected route;
- cybernetic_context says `local_patch_allowed: no`;
- proof matrix is missing;
- forbidden actions or surface budget are missing.

Emit when invoked:

```yaml
fixed_point_receipt:
  selected_route:
  owner:
  prior_route_checked:
  proof_required:
  handoff_result:
```
