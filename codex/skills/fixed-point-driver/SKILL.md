---
name: fixed-point-driver
description: "Drive code toward one canonical owner and verified normal form. In Minimum Behavioral Kernel mode, compile exactly one selected realization from the fixed campaign base, prove kernel conformance, and return on any new observation or semantic distinction. Never patch delivery directly."
metadata:
  version: "4.0.0"
---

# Fixed-Point Driver

## General mission

Reach:

```text
one canonical owner
no unresolved counterexample
no shadow truth
no unnecessary surface
current proof
```

## Minimum Behavioral Kernel mode

Activate when the handoff contains:

```yaml
kernel_realization_handoff:
  campaign_id:
  campaign_base_sha:
  accepted_kernel_ref:
  selected_design:
  permitted_owners:
  surfaces_to_retire:
  hard_surface_ceiling:
  proof_laws:
  worktree:
```

Rules:

- Work only in the named realization worktree.
- Start from campaign base.
- Implement the accepted kernel, not raw review findings.
- Add no behavioral distinction absent from the kernel.
- Retire superseded surfaces named by the design.
- Map every construct to kernel elements.
- Map every proof to kernel laws.
- Stop on a new observation.
- Do not incrementally patch after kernel change.
- Do not edit, commit, or push delivery.

Output:

```yaml
kernel_realization_result:
  campaign_id:
  design_id:
  realization_patch_ref:
  kernel_conformance:
  code_construct_map:
  surfaces_retired:
  semantic_surface:
  proof_law_map:
  new_observations: []
  result:
    valid |
    invalid |
    return_to_kernel |
    blocked
```
