---
name: verification-closure
description: "Make the final current-artifact readiness decision. For Minimum Behavioral Kernel `$resolve`, require a current MBKC-v1, fixed campaign base, accepted kernel, whole-PR realization, semantic-surface conservation, zero orphan code, compressed proof, current holdouts, physical commit/push, and explicit closure horizon."
metadata:
  version: "4.0.0"
---

# Verification Closure

## General mission

Decide whether the current artifact is actually ready.

## Kernel-mode closure

Require:

```text
.ledger/resolve/c3/mbkc.json
certificate_version = MBKC-v1
campaign_base unchanged
review-ready baseline unchanged
kernel accepted
realization compiled from campaign base
orphan code constructs = 0
wound-specific tests = 0
semantic-surface gate passed
proof current
kernel holdout clean
conformance holdout clean
PR sweep current
physical commit/push current
```

Closure verdicts:

```text
kernel_accepted
conformance_closed_for_tuple
terminal_closed
blocked
```

Reject:

- unqualified `complete`;
- tuple closure presented as terminal;
- silent scope expansion;
- realization from a prior closure head;
- manual delivery mutation;
- stale MBKC;
- proof mapped to review wounds instead of kernel laws;
- code or test surface without kernel mapping.

Output:

```yaml
verification_closure:
  mbkc_gate:
  campaign_gate:
  kernel_gate:
  realization_gate:
  semantic_surface_gate:
  proof_compression_gate:
  holdout_gate:
  delivery_gate:
  closure_horizon:
  verdict:
```
