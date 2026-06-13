# Review Compression Handoff

When `$resolve` supplies a `review_compression_packet`, `$fixed-point-driver` should treat it as the cluster-level input, not as a queue of separate review comments.

## Consume

```yaml
review_compression_packet:
  cluster_id:
  counterexamples:
  selected_normal_form:
  proof_matrix:
  implementation_handoff:
  closure_rule:
```

## Rules

- Do not re-expand one selected normal form into independent local patches.
- Preserve selected owner and forbidden actions unless fresh evidence invalidates them.
- If the same cluster reappears after implementation, treat the selected normal form as falsified and route back to `$review-compression-compiler`.
- If selected normal form is `add-new-surface`, require abstraction rent to be paid.
- If proof matrix is too broad or missing, route validation-only before mutation.
