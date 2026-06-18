# Cleanroom Resolve Handoff

When invoked by `$resolve`, `$fixed-point-driver` may implement only a compiled delivery permit.

Reject handoff when:

- delivery is frozen and no DPR-v1 recipe exists;
- no RGR-V4-COMPILED-DELIVERY-PERMIT exists;
- counterexample contract is missing;
- non-branch-liable findings are included in recipe;
- falsified route family remains selected;
- ablation certificate is missing when closure is requested;
- actual implementation would require lab-only artifacts;
- new surface exceeds recipe;
- proof matrix is missing.

Implement the recipe, not review comments.

Emit:

```yaml
fixed_point_receipt:
  compiled_permit_id:
  recipe_id:
  implemented_from_frozen_base: yes | no
  lab_commits_cherry_picked: yes | no
  actual_surface_delta:
  recipe_deviation: yes | no
  handoff_result: completed | return_to_compiler | blocked
```
