# Example invocations

## Final readiness

```md
Use $verification-closure for this task.

Verify the current patch using:
- adversarial-reviewer output
- specialist briefings
- current tests and CI evidence

Goal:
- decide whether the artifact set is actually ready
- close or explicitly fail every material gate

Constraints:
- treat reviewer and specialist outputs as signals, not proof
- if briefings conflict, run the narrowest resolving check
- do not redesign or rewrite
```
