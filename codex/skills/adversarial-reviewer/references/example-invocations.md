# Example invocations

## Exhaustive review

```md
Use $adversarial-reviewer for this task.

Perform a full-scope de novo adversarial review.
Do not limit review to the diff.
Treat prior findings as non-binding context only.
Grade:
- complexity delta
- invariant ledger
- foot-gun register
- verification gaps

Return:
- Review Basis
- Material Findings
- Complexity Delta
- Invariant Ledger
- Foot-Gun Register
- Fixed-Point Judgment
- Suggested Next Moves
```

## Re-review after remediation

```md
Use $adversarial-reviewer for this task.

Re-review the current artifact set from scratch after the latest remediation.
Do not assume earlier conclusions still hold.
Only call for structural remediation when an accretive fix is genuinely insufficient.
```
