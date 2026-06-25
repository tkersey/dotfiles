# Policy State Transition

ETR-v1 is the sole authority for advancing EPS-v1.

It binds:

```text
EPG digest
EPS before digest
EPD decision/action
prediction copied from EPG
actual observations/effects
proof and artifact state
potential before/after
surprise classification
result
```

## Surprise routes

```text
none
  predicted route remains valid

expected_variance
  continue only when policy explicitly tolerates the variance

new_branch
  return to policy selection/revision

model_failure
  old policy cannot authorize another material action

intent_failure
  return to source authority
```

## Atomicity

EPS advancement must be atomic with its receipt reference.

A failed validation or write leaves the prior state untouched.

## Negative evidence

Only controller-proven model failure should produce durable action-model negative evidence.
