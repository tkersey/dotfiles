# Example invocations

## Exhaustive hardening with subagents

```md
Use $meta-orchestrator for this task.

Goal: find all impactful changes, keep re-reviewing from scratch, use parallel specialist subagents, and decide whether the current artifact set is actually ready.

Context:
- auth/session.ts
- auth/session.test.ts
- failing CI logs

Constraints:
- preserve the current public API unless structural evidence proves that is insufficient
- keep writes single-threaded and reviewable
- subagents should be read-only and return packet-native briefings
- regenerate the closure handoff packet after every material validation or remediation

Done when:
- the artifact set reaches a material fixed point
- no unresolved critical invariant, material foot-gun, or material complexity hazard remains
- direct closure verification succeeds
```

## Review-only exhaustive pass

```md
Use $meta-orchestrator for this task.

Review the current branch against main.
Use parallel specialist subagents.
Wait for all results.
Run a full-scope de novo adversarial synthesis.
Then emit a canonical Closure Handoff Packet before final verification.
```
