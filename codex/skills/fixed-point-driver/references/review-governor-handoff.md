# Review Governor Handoff

When invoked by `$resolve`, `$fixed-point-driver` must implement the selected governor route, not the review finding queue.

Reject handoff when:

- `review_governor_record` is required but missing;
- same-cluster recurrence lacks `RGR-V2-MUTATION-PERMIT`;
- same-cluster recurrence selected raw `mutate-existing-owner`;
- positive production net embargo failed;
- owner coarseness gate is unknown/failed;
- boundary inventory requires universalist/reduce/distill but handoff is local mutation;
- active negative evidence excludes the selected route;
- proof matrix gate failed;
- forbidden actions or surface budget are missing.

Emit when invoked:

```yaml
fixed_point_receipt:
  selected_route:
  mutation_permit:
  owner:
  prior_route_checked:
  proof_required:
  handoff_result:
```
