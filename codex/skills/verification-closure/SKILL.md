---
name: verification-closure
description: "Make the final current-artifact readiness decision from proof, review, risk, and durable workflow state. For C³ `$resolve`, require a final MRPC-v1 whose patch fingerprint, proof, ablation, holdout, commit, and push all match current delivery state."
metadata:
  version: "3.0.0"
---

# Verification Closure

## Mission

Decide whether the current artifact is actually ready.

## General closure

Require:

```text
current artifact identity
acceptance criteria
proof commands and evidence
review disposition
residual risk
rollback/abort posture
```

## C³ closure

Require:

```text
.ledger/c3/mrpc.json
certificate_version = MRPC-v1
stage = pushed or closed
immutable base matches run
selected patch fingerprint matches applied delivery patch
all proof entries pass
candidate and delivery holdouts contain no unresolved branch liability
ablation.one_minimal = true
orphan_edit_atoms = []
commit SHA matches delivery
push state is current
```

Reject closure when:

- review-derived delivery mutation bypassed the controller;
- a new counterexample was patched instead of triggering recompilation;
- a surviving edit lacks a witness;
- raw commit/push bypassed MRPC gates;
- adjacent findings were silently absorbed;
- the certificate is stale.

Output:

```yaml
verification_closure:
  artifact_state_match:
  mrpc_gate:
  proof_gate:
  holdout_gate:
  minimality_gate:
  delivery_gate:
  residual_risk:
  verdict: ready | blocked
```
