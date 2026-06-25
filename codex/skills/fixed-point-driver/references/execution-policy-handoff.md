# EPG Policy Binding for FPS-v1/FPSR-v1

Reuse the existing fixed-point slice protocol.

When the selected slice comes from EPG runtime, add matching `policy_control` to FPS-v1 and `policy_result` to FPSR-v1.

## Input lineage

```text
policy ID/revision/digest
state ID/digest
decision ID
action ID/kind
commitment-horizon sequence
expected effects/observations
```

## Output lineage

```text
same policy/state/decision/action identity
actual effects
actual observations with evidence refs
prediction invalidation flag
```

The fixed-point driver reports evidence only.

It does not select the next action or advance EPS.

A new observation forces `return_to_frontier`.
