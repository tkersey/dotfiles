# Example invocations

## Full chain
Use `$meta-orchestrator` for this task.

Goal: fix the regression, challenge the patch, and decide if it is ready to merge.
Context:
- auth/session.ts
- auth/session.test.ts
- failing CI logs
Constraints:
- preserve the current public API
- no broad refactor
Done when:
- the root cause is identified
- minimal patch is applied
- review concerns are either resolved or bounded
- readiness is classified with evidence

## Review + verify only
Use `$meta-orchestrator` for this task.

A patch already exists. Challenge the diagnosis and patch, then determine if it is ready to merge.
Focus on:
- unsound assumptions
- invariant breaks
- regression risk
- missing verification
