---
name: fixed-point-driver
description: "Drive implementation, adversarial review, ablation, and proof toward one canonical truth-owner normal form. In C³ `$resolve`, operate only as a disposable candidate generator/verifier in a lab worktree and never mutate delivery or consume raw review findings. Use for repeated invariant repair, normal-form discovery, candidate verification, or fixed-point closure."
metadata:
  version: "3.0.0"
---

# Fixed-Point Driver

## Mission

Reach a state where:

```text
one canonical owner
no unresolved counterexample
no duplicate truth surface
no unwarranted additive scaffold
current proof
```

## Modes

### General mode

Use the ordinary loop:

```text
frame
-> extract truth units
-> compare validate/no-change/subtractive/owner/representation routes
-> implement one bounded route
-> adversarial review
-> ablate
-> prove
-> close or reopen
```

### C³ candidate mode

Activate when the handoff contains:

```yaml
candidate_handoff:
  run_id:
  immutable_base:
  candidate_id:
  route_class:
  counterexample_basis:
  semantic_cost_budget:
  worktree:
```

Hard rules:

- Work only in the named lab/candidate worktree.
- Never edit delivery.
- Never consume raw review comments as tasks.
- Implement one route class from the immutable base.
- Verify the complete counterexample basis and original acceptance.
- Record every new truth owner, state dimension, branch, helper, proof obligation, and retained surface.
- Return a candidate patch, semantic-cost vector, proof evidence, and defeated alternatives.
- If a new counterexample appears, return it; do not patch around it.
- Do not commit/push delivery.
- Do not claim final closure.

Output:

```yaml
candidate_result:
  candidate_id:
  route_family:
  patch_ref:
  verification:
    counterexamples_pass:
    acceptance_pass:
    regressions_pass:
    proof_current:
  semantic_cost:
  negative_route:
  new_counterexamples: []
  result: valid | invalid | blocked
```
