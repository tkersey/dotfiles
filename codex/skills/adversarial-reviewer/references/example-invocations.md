# Example invocations

## Exhaustive re-review after a fix

```md
Use $adversarial-reviewer for this task.

Review the current state of:
- auth/session.ts
- auth/session.test.ts
- any directly implicated helpers or config

Mode:
- full-scope
- de novo
- exhaustive
- material

Goal:
- re-review from scratch after the latest remediation
- do not trust prior passes
- find anything still materially wrong
- decide whether the current state appears at a material fixed point

Return:
- Review Basis
- Material Findings
- Non-Material Concerns
- Verification Gaps
- Fixed-Point Judgment
- Suggested Next Moves
- Residual Uncertainty
```

## Audit a stabilized patch before closure

```md
Use $adversarial-reviewer for this task.

Artifact set:
- src/cache.py
- tests/test_cache.py
- migration notes

Task:
Perform a full-scope de novo adversarial review of the current artifact set.
Do not limit review to the diff.
Treat prior findings as non-binding context only.
Focus on correctness, compatibility, and verification sufficiency.
End with a fixed-point judgment.
```
