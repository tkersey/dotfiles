# Example invocations

Tail-weighted note: end with `Reviewer Bottom Line`.

## Exhaustive re-review with complexity, invariants, and foot-guns

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
- invariant-graded
- hazard-seeking

Goal:
- re-review from scratch after the latest remediation
- do not trust prior passes
- find anything still materially wrong
- grade the complexity delta
- issue an invariant ledger
- discover any remaining foot-guns
- decide whether the current state appears at a material fixed point

Remediation guidance:
- do not let accretive discipline suppress findings
- if a finding can be fixed narrowly, recommend the narrowest consequential remediation
- if broader redesign is required, justify why the issue is structural

Return:
- Review Basis
- Material Findings
- Complexity Delta
- Invariant Ledger
- Foot-Gun Register
- Non-Material Concerns
- Verification Gaps
- Residual Uncertainty
- Change Agenda
- Fixed-Point Judgment
- Reviewer Bottom Line
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
Focus on correctness, compatibility, invariant preservation, complexity pressure, and verification sufficiency.
Keep discovery unconstrained, but keep remediation guidance accretive unless a material issue is structural.
End with a fixed-point judgment.
```

## Force explicit foot-gun and invariant grading

```md
Use $adversarial-reviewer for this task.

Review this change exhaustively.
For the final output:
- enumerate critical, major, and supporting invariants
- mark each invariant as preserved, strained, broken, or unknown
- create a foot-gun register with ease of misuse and detectability
- classify remediation posture for every material finding as:
  - validating-check-only
  - accretive-remediation
  - structural-remediation

Do not recommend structural-remediation unless you can explain why a narrower accretive fix would be insufficient.
```
