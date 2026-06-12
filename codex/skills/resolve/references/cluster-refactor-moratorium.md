# Cluster Refactor Moratorium

Three adjacent findings are not three tasks. They are evidence of an owner, abstraction, or boundary problem.

## Trigger

If three review findings in the same subsystem, file, protocol, state machine, parser/validator, lifecycle, retry/idempotency path, cache/index, impossible-state family, or truth owner appear in one `$resolve` run, stop point-fix mutation for that cluster.

## Required artifact

```yaml
cluster_refactor_moratorium:
  cluster_id:
  review_item_ids:
  suspected_owner:
  invariant_or_protocol:
  local_patches_already_attempted:
  duplicate_or_shadow_surfaces:
  selected_route:
    no-change | validate-only | delete-collapse-canonicalize | refactor-existing-owner | mutate-existing-owner | add-new-surface | blocked
  required_skill:
    complexity-mitigator | simplify-and-refactor-code-isomorphically | reduce | universalist | fixed-point-driver
  proof_required:
```

## Release conditions

The moratorium lifts only when:

- the selected skill produces a route and proof plan;
- the cluster is proven to be unrelated false grouping;
- or the root reports a blocker and stops mutation.

## Defaults

- If the cluster is hard to understand, start with `complexity-mitigator`.
- If the cluster duplicates or preserves pass-through/shadow surface, start with `simplify-and-refactor-code-isomorphically`.
- If the cluster is caused by layer/tooling/config abstraction tax, start with `reduce`.
- If the cluster lacks a boundary artifact, start with `universalist`.
- If the cluster is already coupled and mutation-bound, route to `fixed-point-driver`.
