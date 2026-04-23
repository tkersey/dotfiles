# Example invocations

## Final closure after exhaustive review

```md
Use $verification-closure for this task.

Verify the current patch using the reviewer outputs and specialist briefings.

Inputs:
- adversarial-reviewer output
- invariant_auditor briefing
- hazard_hunter briefing
- complexity_auditor briefing
- failing CI logs
- auth/session.ts
- auth/session.test.ts

Goal:
- decide whether the artifact set is actually ready to merge
- close or explicitly fail every material gate

Constraints:
- preserve the current public API
- do not redesign or rewrite
- if briefings conflict, run the narrowest resolving check and say so explicitly

Return:
- Verification Target
- Evidence Inputs
- Closure Gate Ledger
- Evidence Run
- Results
- Fixed-Point Test
- Readiness
- Residual Risks
- Next Checks
```

## Closure with optional read-only subagents

```md
Use $verification-closure for this task.

Goal:
- make a final readiness decision on the current branch
- use read-only specialist subagents only if closure signals are stale, mixed, or incomplete

Context:
- current branch vs main
- failing integration logs
- partial reviewer output

Constraints:
- use verification_auditor and invariant_auditor only if needed
- wait for all relevant briefings before the final judgment
- keep closure single-threaded and evidence-backed
```

## Release gate for a migration

```md
Use $verification-closure for this task.

Verify whether the migration is ready for release.
Consume any invariant, hazard, and verification briefings already produced.

Focus on:
- direct changed-path proof
- rollback and retry hazards
- persistence invariants
- one plausible regression surface

Return a readiness state of ready, conditionally ready, not ready, or indeterminate.
```
