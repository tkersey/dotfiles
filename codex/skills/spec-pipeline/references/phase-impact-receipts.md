# Phase Impact Receipts

Use compact receipts for internal companion phases:

```yaml
spec_gate_receipt:
spec_challenge_receipt:
spec_fresh_eyes_receipt:
spec_lint_receipt:
```

Each receipt should record whether the phase changed the decision/spec/proof/scope/risk, blocked handoff, or passed with no delta.

Do not chase standalone companion activations. Measure phase impact.
