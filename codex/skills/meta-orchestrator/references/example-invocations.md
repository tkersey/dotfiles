# Example invocations

## Exhaustive hardening with posture-aware routing

```md
Use $meta-orchestrator for this task.

Goal: find all impactful changes, re-review from scratch after every validating check or fix, and continue until the code reaches a material fixed point.
Context:
- auth/session.ts
- auth/session.test.ts
- failing CI logs

Constraints:
- preserve the current public API unless a structural issue proves that is insufficient
- keep each remediation reviewable and evidence-backed

Routing rules:
- if the reviewer says validating-check-only, run the narrowest high-signal check first
- if the reviewer says accretive-remediation, make the narrowest consequential fix
- if the reviewer says structural-remediation, justify why a narrower fix is insufficient before broadening scope

Done when:
- material findings are exhausted under full-scope de novo review
- direct verification passes
- no unresolved material issue remains
```

## Patch exists, route reviewer findings explicitly

```md
Use $meta-orchestrator for this task.

A patch already exists. Re-litigate it de novo in full-scope adversarial mode after every validating check or remediation.
Do not limit review to the diff.

When adversarial-reviewer returns findings:
- consume remediation posture explicitly
- validating-check-only -> targeted validation subpass
- accretive-remediation -> rigor-doctrine narrow remediation
- structural-remediation -> rigor-doctrine structural remediation or needs-decision if constraints forbid it

Keep looping until a full review yields no unresolved material findings and final closure verification no longer reopens the loop.
```

## Structural issue under tight scope constraints

```md
Use $meta-orchestrator for this task.

Goal: harden this change exhaustively, but do not hide structural problems behind narrow patches.

Constraints:
- preserve the public API if possible
- no broad redesign unless the issue is materially structural and you can justify it

If the reviewer classifies a material issue as structural-remediation:
- explain why accretive remediation is insufficient
- either perform the narrowest necessary structural change
- or return needs-decision with evidence if the current constraints forbid it

Re-review de novo after every check or fix.
```
