# Example invocations

## Exhaustive hardening loop
Use `$meta-orchestrator` for this task.

Goal: fix the regression, re-litigate the patch de novo after each remediation, and continue until the code reaches a material fixed point.
Context:
- auth/session.ts
- auth/session.test.ts
- failing CI logs
Constraints:
- preserve the current public API
- no speculative redesign
Done when:
- the root cause is identified
- material findings are remediated accretively
- each loop includes a full-scope adversarial re-review
- direct verification passes
- no unresolved material issue remains

## Patch exists, exhaustively harden it
Use `$meta-orchestrator` for this task.

A patch already exists. Re-litigate it de novo in full-scope adversarial mode, remediate material findings, and keep looping until a full review yields no new material issues and closure verification no longer reopens the loop.
Focus on:
- unsound assumptions
- invariant breaks
- regression risk
- missing verification
- newly implicated surfaces
